import os
from enum import Enum
from pathlib import Path
from typing import Tuple, List, Optional, Dict, Any
from urllib.parse import urlparse
from core.logger import logger
from core.permissions import PermissionManager, PermissionCategory

class ActionRisk(str, Enum):
    SAFE = "SAFE"
    CONFIRMATION_REQUIRED = "CONFIRMATION_REQUIRED"
    BLOCKED = "BLOCKED"

class SecurityPolicy:
    """
    Política de seguridad estricta para interacción con el SO en JARVIS v3.1.
    Principio fundamental: Modelo ALLOWLIST (Fail-Closed).
    Cualquier acción o comando no explícitamente autorizado se clasifica como BLOCKED por defecto.
    Eliminación de archivos permanentemente prohibida para el asistente.
    """
    
    ALLOWED_DIRECTORIES = ["Desktop", "Documents", "Downloads", "Pictures", "Music", "Videos"]

    FOLDER_ALIASES: Dict[str, List[str]] = {
        "desktop": ["Desktop", "Escritorio"],
        "documents": ["Documents", "Documentos", "Mis documentos", "Doc"],
        "downloads": ["Downloads", "Descargas"],
        "pictures": ["Pictures", "Imágenes", "Imagenes", "Fotos", "Mis imágenes"],
        "music": ["Music", "Música", "Musica", "Mi música"],
        "videos": ["Videos", "Vídeos", "Mis vídeos"],
    }
    
    # Acciones estrictamente autorizadas sin confirmación previa
    SAFE_ACTIONS = {
        # Desktop y archivos
        "open_application",
        "focus_application",
        "close_application",
        "close_window",
        "open_url",
        "open_file",
        "open_folder",
        "list_files",
        "get_active_application",
        "get_running_applications",
        "create_text_file",
        "read_text_file",
        "create_pdf",
        "create_docx",
        "generate_image",
        "analyze_screen",
        "search_files",
        # Sistema
        "set_volume",
        "get_current_datetime",
        "current_datetime",
        "get_location",
        "parse_relative_time",
        "parse_time",
        "ping",
        # Multimedia
        "play_music",
        "search_music",
        "pause_music",
        "resume_music",
        "skip_music",
        "get_now_playing",
        "get_music_queue",
        "clear_music_queue",
        "recommend_music",
        "search_videos",
        # Memoria
        "remember_info",
        "recall_memories",
        "forget_memory",
        "get_memory_summary",
        "export_memory",
        # Recordatorios y Tareas
        "create_reminder",
        "list_reminders",
        "snooze_reminder",
        "complete_reminder",
        "delete_reminder",
        "clear_all_pending",
        "get_pending_summary",
        "create_task",
        "list_tasks",
        "complete_task",
        "delete_task",
        # Web
        "read_webpage",
        "web_search",
        "search_youtube",
        # Automatización y Workflows Multi-paso (Fase 18)
        "execute_workflow",
        "get_daily_briefing"
    }

    # Acciones del sistema que requieren confirmación explícita del usuario
    CONFIRMATION_ACTIONS = {
        "system_shutdown",
        "system_restart",
        "system_sleep",
        "close_all_applications",
        "clear_memory",
        "clear_all_reminders",
        "clear_all_tasks"
    }

    # Bloqueo total de eliminación de archivos y ejecución arbitraria
    BLOCKED_FILE_ACTIONS = {
        "delete_file",
        "remove_file",
        "delete_folder",
        "unlink",
        "rmdir",
        "remove-item"
    }

    BLOCKED_ACTIONS = {
        *BLOCKED_FILE_ACTIONS,
        "execute_command",
        "run_script",
        "modify_registry",
        "format_disk",
        "powershell",
        "cmd"
    }

    DANGEROUS_PATTERNS = [
        "del /f", "del /s", "del /q", "rmdir", "format", "shutdown", "reg delete",
        "reg add", "powershell -c remove", "powershell -enc", "-encodedcommand",
        "drop table", "truncate", "net user", "taskkill /f /im explorer", "rm -rf",
        ":(){ :|:& };:", "diskpart", "bcdedit", "vssadmin delete shadows", "remove-item",
        "unlink", "os.remove", "shutil.rmtree", "iex(", "invoke-expression", "curl | sh",
        "wget | sh", "bitsadmin", "certutil -urlcache"
    ]

    CONFIRMATION_KEYWORDS = [
        "apaga la pc", "reinicia la pc", "formatea", "cerrar sesión", "limpiar disco"
    ]

    ALLOWED_URL_SCHEMES = ["http", "https"]

    @classmethod
    def _normalize_string(cls, text: str) -> str:
        """Normaliza cadenas eliminando espacios redundantes y caracteres de evasión."""
        if not text:
            return ""
        import re
        # Reemplazar múltiples espacios y caracteres de control/nulos
        clean = re.sub(r'[\x00-\x1f\x7f]', '', text)
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip().lower()

    @classmethod
    def is_dangerous(cls, command_or_action: str) -> bool:
        norm = cls._normalize_string(command_or_action)
        # Búsqueda compacta sin espacios para evitar evasión tipo "d e l / f" o "del   /f"
        no_spaces = norm.replace(" ", "")
        for p in cls.DANGEROUS_PATTERNS:
            p_clean = p.lower()
            p_no_spaces = p_clean.replace(" ", "")
            if p_clean in norm or p_no_spaces in no_spaces:
                return True
        return False

    @classmethod
    def validate_app(cls, app_name: str) -> Tuple[bool, Optional[str], Optional[str]]:
        from core.windows_automation import ApplicationRegistry
        key, info = ApplicationRegistry.resolve_app(app_name)
        if info:
            installed, target = ApplicationRegistry.is_installed(info)
            return True, key, target
        return False, None, None

    @classmethod
    def classify_action(cls, action_name: str, target: str = "") -> ActionRisk:
        """
        Clasifica el riesgo de una acción bajo un modelo ALLOWLIST estricto:
        1. Si contiene patrones peligrosos o está en BLOCKED_ACTIONS -> BLOCKED.
        2. Si requiere confirmación o coincide con CONFIRMATION_ACTIONS -> CONFIRMATION_REQUIRED.
        3. Solo si está explícitamente en SAFE_ACTIONS -> SAFE.
        4. Por defecto (fail-closed) -> BLOCKED.
        """
        act_norm = cls._normalize_string(action_name)
        target_norm = cls._normalize_string(target)

        # 1. Bloqueo explícito de eliminación de archivos y acciones prohibidas
        if act_norm in cls.BLOCKED_ACTIONS or act_norm in cls.BLOCKED_FILE_ACTIONS:
            logger.warning(f"[SecurityPolicy] Acción explícitamente bloqueada: {action_name}")
            return ActionRisk.BLOCKED

        # 2. Detección de encadenamiento de comandos maliciosos (&, &&, ;, |, ||)
        import re
        if re.search(r'[;&|`$]', target):
            logger.warning(f"[SecurityPolicy] Acción bloqueada por encadenamiento de comandos: {target}")
            return ActionRisk.BLOCKED

        # 3. Comprobar si es una acción autorizada que requiere confirmación previa
        if act_norm in cls.CONFIRMATION_ACTIONS:
            return ActionRisk.CONFIRMATION_REQUIRED

        for kw in cls.CONFIRMATION_KEYWORDS:
            if kw in target_norm or kw in act_norm:
                return ActionRisk.CONFIRMATION_REQUIRED

        # 4. Detección de patrones peligrosos en target o acción no confirmada
        if cls.is_dangerous(target_norm) or cls.is_dangerous(act_norm):
            logger.warning(f"[SecurityPolicy] Acción bloqueada por patrón peligroso en target/acción: {action_name} | {target}")
            return ActionRisk.BLOCKED

        # 5. ALLOWLIST: Solo las acciones explícitamente listadas como seguras se permiten
        if act_norm in cls.SAFE_ACTIONS:
            return ActionRisk.SAFE

        # 6. FAIL-CLOSED: Todo lo demás es denegado por defecto
        logger.warning(f"[SecurityPolicy] Acción denegada por no estar en allowlist (Fail-Closed): {action_name}")
        return ActionRisk.BLOCKED

    @classmethod
    def validate_url(cls, url: str) -> Tuple[bool, Optional[str], Optional[str]]:
        if not url or not url.strip():
            return False, None, "INVALID_URL"
        
        u = url.strip()
        u_lower = u.lower()
        
        blocked_schemes = ["javascript:", "file:", "data:", "powershell:", "vbscript:", "cmd:", "about:"]
        for bs in blocked_schemes:
            if u_lower.startswith(bs):
                logger.warning(f"[SecurityPolicy] Esquema peligroso bloqueado: {bs}")
                return False, None, "BLOCKED_ACTION"

        if u_lower.startswith(("http://", "https://")):
            parsed = urlparse(u)
            if not parsed.netloc:
                return False, None, "INVALID_URL"
            return True, u, None
        
        if ":" in u and not u.startswith(("//", "/")):
            parsed = urlparse(u)
            if parsed.scheme.lower() not in cls.ALLOWED_URL_SCHEMES:
                return False, None, "BLOCKED_ACTION"

        normalized = "https://" + u
        parsed = urlparse(normalized)
        if not parsed.netloc:
            return False, None, "INVALID_URL"
        return True, normalized, None

    @classmethod
    def get_actual_user_dir(cls, dir_name: str = "Desktop") -> Path:
        """
        Obtiene la ruta real de una carpeta de usuario, considerando sincronización de OneDrive
        en Windows y variantes de nombres en español e inglés.
        """
        home = Path.home().resolve()
        key = dir_name.lower().strip()
        candidates = list(cls.FOLDER_ALIASES.get(key, [dir_name]))
        if dir_name not in candidates:
            candidates.insert(0, dir_name)

        onedrive_root = home / "OneDrive"

        # 1. Probar OneDrive con todos los alias
        if onedrive_root.exists():
            for cand in candidates:
                p = onedrive_root / cand
                if p.exists():
                    return p.resolve()

        # 2. Probar home con todos los alias
        for cand in candidates:
            p = home / cand
            if p.exists():
                return p.resolve()

        # 3. Fallback: si existe OneDrive preferir OneDrive, sino home
        if onedrive_root.exists():
            return (onedrive_root / candidates[0]).resolve()
        return (home / candidates[0]).resolve()

    @classmethod
    def validate_path_access(cls, requested_path: str, must_exist: bool = False) -> Tuple[bool, Optional[Path], Optional[str]]:
        """
        Valida que una ruta esté estrictamente dentro de las carpetas de usuario autorizadas
        (Desktop, Documents, Downloads, etc.), soportando OneDrive y variantes de nombres.
        """
        if not PermissionManager.is_granted(PermissionCategory.FILES):
            return False, None, "PERMISSION_DENIED"

        if not requested_path or not requested_path.strip():
            return False, None, "INVALID_PATH"

        # Prevenir Path Traversal
        if ".." in requested_path:
            return False, None, "BLOCKED_ACTION"

        home = Path.home().resolve()
        loc_str = requested_path.lower().strip()
        desktop_dir = cls.get_actual_user_dir("Desktop")

        if loc_str in ["desktop", "escritorio"]:
            raw_target = desktop_dir
        elif loc_str in ["documents", "documentos", "doc", "mis documentos"]:
            raw_target = cls.get_actual_user_dir("Documents")
        elif loc_str in ["downloads", "descargas"]:
            raw_target = cls.get_actual_user_dir("Downloads")
        elif loc_str in ["pictures", "imagenes", "imágenes", "fotos"]:
            raw_target = cls.get_actual_user_dir("Pictures")
        elif loc_str in ["music", "música", "musica"]:
            raw_target = cls.get_actual_user_dir("Music")
        else:
            raw_target = Path(requested_path).expanduser()

        # Si es una ruta relativa o solo un nombre de archivo (ej. 'nota.txt'), guardar por defecto en Desktop
        if not raw_target.is_absolute():
            resolved = (desktop_dir / raw_target).resolve()
        else:
            resolved = raw_target.resolve()

        # Comprobar que esté dentro de una carpeta permitida
        is_authorized = False
        allowed_roots = []
        for allowed in cls.ALLOWED_DIRECTORIES:
            actual = cls.get_actual_user_dir(allowed)
            allowed_roots.append(actual)
            
            key = allowed.lower().strip()
            aliases = cls.FOLDER_ALIASES.get(key, [allowed])
            for alias in aliases:
                allowed_roots.append((home / alias).resolve())
                allowed_roots.append((home / "OneDrive" / alias).resolve())

        for allowed_dir in allowed_roots:
            # Si el directorio existe o si estamos en modo creación (must_exist=False), validar inclusión
            try:
                resolved.relative_to(allowed_dir)
                is_authorized = True
                break
            except ValueError:
                continue

        if not is_authorized:
            try:
                if resolved == home or resolved == desktop_dir:
                    is_authorized = True
            except ValueError:
                pass

        if not is_authorized:
            logger.warning(f"[SecurityPolicy] Acceso fuera de carpetas autorizadas denegado: {resolved}")
            return False, None, "BLOCKED_ACTION"

        if must_exist and not resolved.exists():
            return False, None, "INVALID_PATH"

        return True, resolved, None
