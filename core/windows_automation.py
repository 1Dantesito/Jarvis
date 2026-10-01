import os
import re
import time
import shutil
import subprocess
import webbrowser
import ctypes
import psutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from core.security import SecurityPolicy, ActionRisk
from core.logger import logger
from core.permissions import PermissionManager, PermissionCategory

class ApplicationRegistry:
    """
    Registro y resolución exhaustiva de aplicaciones de Windows con alias y ejecutables.
    """
    
    APPS = {
        "chrome": {
            "name": "Google Chrome",
            "executables": ["chrome.exe", "chrome"],
            "process_names": ["chrome.exe"],
            "uri": None,
            "fallback_paths": [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ]
        },
        "edge": {
            "name": "Microsoft Edge",
            "executables": ["msedge.exe", "msedge"],
            "process_names": ["msedge.exe"],
            "uri": None,
            "fallback_paths": [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
            ]
        },
        "spotify": {
            "name": "Spotify",
            "executables": ["spotify.exe"],
            "process_names": ["spotify.exe"],
            "uri": "spotify:",
            "fallback_paths": [
                os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe")
            ]
        },
        "calc": {
            "name": "Calculadora",
            "executables": ["calc.exe", "calc", "CalculatorApp.exe"],
            "process_names": ["CalculatorApp.exe", "calc.exe", "Calculator.exe"],
            "uri": "calculator:",
            "fallback_paths": [r"C:\Windows\System32\calc.exe"]
        },
        "notepad": {
            "name": "Bloc de notas",
            "executables": ["notepad.exe", "notepad"],
            "process_names": ["notepad.exe", "Notepad.exe"],
            "uri": None,
            "fallback_paths": [r"C:\Windows\System32\notepad.exe"]
        },
        "explorer": {
            "name": "Explorador de archivos",
            "executables": ["explorer.exe"],
            "process_names": ["explorer.exe"],
            "uri": None,
            "fallback_paths": [r"C:\Windows\explorer.exe"]
        },
        "cmd": {
            "name": "Símbolo del sistema",
            "executables": ["cmd.exe"],
            "process_names": ["cmd.exe"],
            "uri": None,
            "fallback_paths": [r"C:\Windows\System32\cmd.exe"]
        },
        "taskmgr": {
            "name": "Administrador de tareas",
            "executables": ["taskmgr.exe"],
            "process_names": ["Taskmgr.exe", "taskmgr.exe"],
            "uri": None,
            "fallback_paths": [r"C:\Windows\System32\taskmgr.exe"]
        },
        "settings": {
            "name": "Configuración de Windows",
            "executables": ["SystemSettings.exe"],
            "process_names": ["SystemSettings.exe"],
            "uri": "ms-settings:",
            "fallback_paths": []
        },
        "vscode": {
            "name": "Visual Studio Code",
            "executables": ["code.exe", "code"],
            "process_names": ["Code.exe", "code.exe"],
            "uri": "vscode:",
            "fallback_paths": [
                os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe")
            ]
        },
        "opera": {
            "name": "Opera",
            "executables": ["opera.exe", "launcher.exe"],
            "process_names": ["opera.exe"],
            "uri": None,
            "fallback_paths": [
                os.path.expandvars(r"%LOCALAPPDATA%\Programs\Opera GX\opera.exe"),
                os.path.expandvars(r"%LOCALAPPDATA%\Programs\Opera\opera.exe"),
                r"C:\Program Files\Opera\launcher.exe",
                r"C:\Program Files\Opera GX\launcher.exe"
            ]
        },
        "operagx": {
            "name": "Opera GX",
            "executables": ["opera.exe", "launcher.exe"],
            "process_names": ["opera.exe"],
            "uri": None,
            "fallback_paths": [
                os.path.expandvars(r"%LOCALAPPDATA%\Programs\Opera GX\opera.exe"),
                r"C:\Program Files\Opera GX\launcher.exe"
            ]
        },
        "brave": {
            "name": "Brave",
            "executables": ["brave.exe"],
            "process_names": ["brave.exe"],
            "uri": None,
            "fallback_paths": [
                r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe")
            ]
        },
        "firefox": {
            "name": "Mozilla Firefox",
            "executables": ["firefox.exe"],
            "process_names": ["firefox.exe"],
            "uri": None,
            "fallback_paths": [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
            ]
        },
        "desktop": {
            "name": "Escritorio",
            "executables": ["explorer.exe"],
            "process_names": ["explorer.exe"],
            "uri": None,
            "fallback_paths": [r"C:\Windows\explorer.exe"]
        }
    }

    ALIASES = {
        "navegador": "chrome",
        "browser": "chrome",
        "google": "chrome",
        "google chrome": "chrome",
        "microsoft edge": "edge",
        "opera": "opera",
        "opera gx": "operagx",
        "operagx": "operagx",
        "navegador opera": "opera",
        "brave": "brave",
        "firefox": "firefox",
        "mozilla": "firefox",
        "mozilla firefox": "firefox",
        "calculadora": "calc",
        "calculator": "calc",
        "bloc de notas": "notepad",
        "block de notas": "notepad",
        "editor de texto": "notepad",
        "explorador": "explorer",
        "explorador de archivos": "explorer",
        "archivos": "explorer",
        "mis archivos": "explorer",
        "carpeta": "explorer",
        "carpetas": "explorer",
        "escritorio": "desktop",
        "desktop": "desktop",
        "pestaña del escritorio": "desktop",
        "pestañas del escritorio": "desktop",
        "pestanas del escritorio": "desktop",
        "ventana del escritorio": "desktop",
        "consola": "cmd",
        "terminal": "cmd",
        "command prompt": "cmd",
        "administrador de tareas": "taskmgr",
        "gestor de tareas": "taskmgr",
        "configuracion": "settings",
        "configuración": "settings",
        "ajustes": "settings",
        "codigo": "vscode",
        "código": "vscode",
        "vs code": "vscode",
        "visual studio code": "vscode"
    }

    @classmethod
    def resolve_app(cls, query: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        clean = query.lower().strip()
        
        if clean in cls.APPS:
            return clean, cls.APPS[clean]
            
        if clean in cls.ALIASES:
            canonical = cls.ALIASES[clean]
            return canonical, cls.APPS[canonical]

        for key, info in cls.APPS.items():
            if clean in info["name"].lower() or info["name"].lower() in clean:
                return key, info
            for exe in info["executables"]:
                if clean == exe.lower().replace(".exe", "") or clean == exe.lower():
                    return key, info

        for alias, canonical in cls.ALIASES.items():
            if alias in clean or clean in alias:
                return canonical, cls.APPS[canonical]

        return None, None

    @classmethod
    def is_installed(cls, app_info: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        for exe in app_info["executables"]:
            p = shutil.which(exe)
            if p:
                return True, p
                
        for fb in app_info.get("fallback_paths", []):
            if os.path.isfile(fb):
                return True, fb

        if app_info.get("uri"):
            return True, app_info["uri"]

        return False, None

class WindowsAutomationProvider:
    """
    Proveedor unificado de automatización de Windows con soporte para ejecución segura,
    creación/lectura de archivos y control de procesos.
    """
    
    CRITICAL_SYSTEM_PROCESSES = {
        "explorer.exe", "svchost.exe", "csrss.exe", "winlogon.exe", 
        "smss.exe", "lsass.exe", "services.exe", "dwm.exe", "system"
    }

    @classmethod
    def find_running_process(cls, app_info: Dict[str, Any]) -> Tuple[bool, Optional[int]]:
        target_names = [p.lower() for p in app_info.get("process_names", [])]
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                p_name = proc.info.get('name', '')
                if p_name and p_name.lower() in target_names:
                    return True, proc.info['pid']
        except Exception as e:
            logger.debug(f"[WindowsAutomation] Error listando procesos: {e}")
        return False, None

    @classmethod
    def get_running_applications(cls) -> Dict[str, Any]:
        running_apps = []
        try:
            active_proc_names = {p.info['name'].lower() for p in psutil.process_iter(['name']) if p.info.get('name')}
            for key, info in ApplicationRegistry.APPS.items():
                for p_name in info.get("process_names", []):
                    if p_name.lower() in active_proc_names:
                        running_apps.append({
                            "key": key,
                            "name": info["name"]
                        })
                        break
        except Exception as e:
            logger.error(f"[WindowsAutomation] Error al obtener apps en ejecución: {e}")

        summary = f"Hay {len(running_apps)} aplicaciones autorizadas en ejecución: " + ", ".join([a["name"] for a in running_apps]) if running_apps else "No hay aplicaciones autorizadas abiertas."
        return {
            "success": True,
            "apps": running_apps,
            "running_apps": running_apps,
            "count": len(running_apps),
            "summary": summary
        }

    @classmethod
    def open_application(cls, app_name: str) -> Dict[str, Any]:
        canonical_key, app_info = ApplicationRegistry.resolve_app(app_name)
        if not app_info:
            return {
                "success": False,
                "status": "APP_NOT_ALLOWED",
                "error_code": "APP_NOT_ALLOWED",
                "message": f"La aplicación '{app_name}' no está en la lista de aplicaciones seguras autorizadas."
            }

        # Manejo especial para explorador y escritorio:
        # explorer.exe siempre está activo en Windows como shell. Para abrir ventanas/pestañas de archivos o escritorio
        # debemos invocar explorer.exe directamente en lugar de solo enfocar el proceso de fondo.
        if canonical_key in ["explorer", "desktop"]:
            try:
                if canonical_key == "desktop":
                    desktop_dir = SecurityPolicy.get_actual_user_dir("Desktop")
                    subprocess.Popen(f'explorer.exe "{desktop_dir}"')
                    msg = "Abriendo tu Escritorio en el Explorador de Windows."
                else:
                    subprocess.Popen("explorer.exe")
                    msg = "Abriendo el Explorador de archivos."
                return {
                    "success": True,
                    "status": "APP_OPENED",
                    "app": app_info["name"],
                    "message": msg
                }
            except Exception as e:
                logger.error(f"[WindowsAutomation] Error abriendo {app_info['name']}: {e}")
                return {
                    "success": False,
                    "status": "EXECUTION_FAILED",
                    "message": f"No pude abrir {app_info['name']} ({e})."
                }

        is_running, pid = cls.find_running_process(app_info)
        if is_running:
            cls.focus_application(canonical_key)
            return {
                "success": True,
                "status": "APP_ALREADY_RUNNING",
                "app": app_info["name"],
                "message": f"{app_info['name']} ya estaba abierto. Lo traje al frente."
            }

        is_inst, target = ApplicationRegistry.is_installed(app_info)
        if not is_inst or not target:
            return {
                "success": False,
                "status": "APP_NOT_INSTALLED",
                "message": f"No encontré {app_info['name']} instalado en tu equipo."
            }

        try:
            if target.endswith(":"):
                os.system(f"start {target}")
            else:
                subprocess.Popen(target, shell=True)

            logger.info(f"[WindowsAutomation] Aplicación abierta con éxito: {app_info['name']} ({target})")
            return {
                "success": True,
                "status": "APP_OPENED",
                "app": app_info["name"],
                "message": f"Abriendo {app_info['name']}."
            }
        except Exception as e:
            logger.error(f"[WindowsAutomation] Error abriendo {app_info['name']}: {e}")
            return {
                "success": False,
                "status": "EXECUTION_FAILED",
                "message": f"No pude iniciar {app_info['name']} ({e})."
            }

    @classmethod
    def focus_application(cls, app_name: str) -> Dict[str, Any]:
        canonical_key, app_info = ApplicationRegistry.resolve_app(app_name)
        if not app_info:
            return {
                "success": False,
                "status": "APP_NOT_ALLOWED",
                "message": f"La aplicación '{app_name}' no está autorizada."
            }

        is_running, pid = cls.find_running_process(app_info)
        if not is_running:
            return {
                "success": False,
                "status": "APP_NOT_RUNNING",
                "message": f"No encuentro {app_info['name']} abierto. ¿Quieres que lo abra?"
            }

        try:
            from ctypes import wintypes
            user32 = ctypes.windll.user32
            found_hwnd = None

            def _enum_window_callback(hwnd, extra):
                nonlocal found_hwnd
                if user32.IsWindowVisible(hwnd):
                    lpdw_process_id = wintypes.DWORD()
                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(lpdw_process_id))
                    if lpdw_process_id.value == pid:
                        found_hwnd = hwnd
                        return False
                return True

            WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
            user32.EnumWindows(WNDENUMPROC(_enum_window_callback), 0)

            if found_hwnd:
                user32.ShowWindow(found_hwnd, 9)
                user32.SetForegroundWindow(found_hwnd)
                user32.BringWindowToTop(found_hwnd)
                return {
                    "success": True,
                    "status": "APP_FOCUSED",
                    "app": app_info["name"],
                    "message": f"Cambiando a {app_info['name']}."
                }
        except Exception as e:
            logger.error(f"[WindowsAutomation] Error en focus_application: {e}")

        return {
            "success": True,
            "status": "APP_FOCUSED",
            "app": app_info["name"],
            "message": f"Cambiando a {app_info['name']}."
        }

    @classmethod
    def close_window(cls, window_title: Optional[str] = None, app_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Cierra una ventana específica abierta en el escritorio por coincidencia de título y/o proceso.
        Usa WM_CLOSE (0x0010) para un cierre limpio y controlado.
        """
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        WM_CLOSE = 0x0010

        target_pids = set()
        target_app_display = None

        if app_name:
            canonical_key, app_info = ApplicationRegistry.resolve_app(app_name)
            if app_info:
                target_app_display = app_info["name"]
                proc_names = [p.lower() for p in app_info.get("process_names", [])]
                for p in psutil.process_iter(["pid", "name"]):
                    try:
                        p_name = p.info.get("name", "")
                        if p_name and p_name.lower() in proc_names:
                            target_pids.add(p.info["pid"])
                    except Exception:
                        pass
            else:
                if not window_title:
                    window_title = app_name

        matching_hwnds = []

        def _enum_close_callback(hwnd, extra):
            if user32.IsWindowVisible(hwnd):
                buf = ctypes.create_unicode_buffer(512)
                user32.GetWindowTextW(hwnd, buf, 512)
                title = buf.value.strip()
                if title:
                    pid = wintypes.DWORD()
                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

                    if target_pids and pid.value not in target_pids:
                        return True

                    if window_title:
                        if window_title.lower() in title.lower():
                            matching_hwnds.append((hwnd, title, pid.value))
                    elif target_pids:
                        matching_hwnds.append((hwnd, title, pid.value))
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(WNDENUMPROC(_enum_close_callback), 0)

        if not matching_hwnds:
            desc = f"con título '{window_title}'" if window_title else ""
            if target_app_display:
                desc += f" de {target_app_display}"
            return {
                "success": False,
                "status": "WINDOW_NOT_FOUND",
                "message": f"No encontré ninguna ventana abierta {desc.strip()}."
            }

        closed_titles = []
        for hwnd, title, pid in matching_hwnds:
            user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
            closed_titles.append(title)

        count = len(closed_titles)
        msg = f"Cerrando la ventana '{closed_titles[0]}'." if count == 1 else f"Cerrando {count} ventanas coincidentes."

        return {
            "success": True,
            "status": "WINDOW_CLOSED",
            "windows_closed": count,
            "closed_titles": closed_titles,
            "message": msg
        }

    @classmethod
    def close_application(cls, app_name: str, window_title: Optional[str] = None) -> Dict[str, Any]:
        if window_title:
            return cls.close_window(window_title=window_title, app_name=app_name)

        canonical_key, app_info = ApplicationRegistry.resolve_app(app_name)
        if not app_info:
            win_res = cls.close_window(window_title=app_name)
            if win_res.get("success"):
                return win_res
            return {
                "success": False,
                "status": "APP_NOT_ALLOWED",
                "message": f"No está permitido cerrar '{app_name}' o no es una aplicación registrada."
            }

        target_procs = [p.lower() for p in app_info.get("process_names", [])]
        if any(p in cls.CRITICAL_SYSTEM_PROCESSES for p in target_procs):
            return {
                "success": False,
                "status": "BLOCKED_CRITICAL_PROCESS",
                "message": f"Acción bloqueada: No se puede cerrar un proceso crítico del sistema operativo."
            }

        closed_count = 0
        try:
            for p in psutil.process_iter(["pid", "name"]):
                p_name = p.info.get("name", "")
                if p_name and p_name.lower() in target_procs:
                    try:
                        p.terminate()
                        closed_count += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

            if closed_count > 0:
                logger.info(f"[WindowsAutomation] Aplicación cerrada: {app_info['name']} ({closed_count} instancias)")
                return {
                    "success": True,
                    "status": "APP_CLOSED",
                    "app": app_info["name"],
                    "instances_closed": closed_count,
                    "message": f"Cerrando {app_info['name']}."
                }
            else:
                win_res = cls.close_window(app_name=app_name)
                if win_res.get("success"):
                    return win_res
                return {
                    "success": False,
                    "status": "APP_NOT_RUNNING",
                    "message": f"{app_info['name']} no está en ejecución."
                }
        except Exception as e:
            logger.error(f"[WindowsAutomation] Error al cerrar {app_info['name']}: {e}")
            return {
                "success": False,
                "status": "EXECUTION_FAILED",
                "message": f"No se pudo cerrar {app_info['name']} ({e})."
            }

    @classmethod
    def create_text_file(cls, filename: str, content: str, location: str = "desktop") -> Dict[str, Any]:
        """
        Crea o escribe un archivo de texto en una carpeta de usuario autorizada.
        """
        loc_str = location.lower().strip()
        target_dir = SecurityPolicy.get_actual_user_dir("Desktop")
        if loc_str in ["documents", "documentos"]:
            target_dir = SecurityPolicy.get_actual_user_dir("Documents")
        elif loc_str in ["downloads", "descargas"]:
            target_dir = SecurityPolicy.get_actual_user_dir("Downloads")

        # Asegurar extensión .txt si no tiene
        clean_name = filename.strip()
        if not any(clean_name.endswith(ext) for ext in [".txt", ".md", ".log", ".json"]):
            clean_name += ".txt"

        target_file_path = target_dir / clean_name
        is_safe, safe_path, err = SecurityPolicy.validate_path_access(str(target_file_path), must_exist=False)
        if not is_safe or not safe_path:
            return {"success": False, "error": err, "message": f"No se permite crear archivos en esa ubicación."}

        try:
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            with open(safe_path, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"[WindowsAutomation] Archivo creado con éxito: {safe_path}")
            return {
                "success": True,
                "file_name": safe_path.name,
                "path": str(safe_path),
                "bytes_written": len(content.encode("utf-8")),
                "message": f"Archivo '{safe_path.name}' creado en tu Escritorio."
            }
        except Exception as e:
            logger.error(f"[WindowsAutomation] Error creando archivo: {e}")
            return {"success": False, "error": str(e), "message": f"Error al escribir el archivo: {e}"}

    @classmethod
    def read_text_file(cls, file_path: str) -> Dict[str, Any]:
        """
        Lee el contenido de un archivo de texto en las carpetas autorizadas.
        """
        is_safe, safe_path, err = SecurityPolicy.validate_path_access(file_path, must_exist=True)
        if not is_safe or not safe_path:
            return {"success": False, "error": err, "message": f"No se puede acceder al archivo '{file_path}'."}

        try:
            with open(safe_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(4000)

            return {
                "success": True,
                "file_name": safe_path.name,
                "content": content,
                "message": f"Contenido de '{safe_path.name}': {content[:150]}..."
            }
        except Exception as e:
            logger.error(f"[WindowsAutomation] Error leyendo archivo: {e}")
            return {"success": False, "error": str(e), "message": f"No se pudo leer el archivo: {e}"}

    @classmethod
    def search_files(cls, query: str, location: Optional[str] = None) -> Dict[str, Any]:
        clean_query = query.lower().strip()
        if not clean_query:
            return {"success": False, "count": 0, "items": [], "message": "Por favor especifica un nombre o término de búsqueda."}

        # Validar consulta con política de seguridad estricta
        if SecurityPolicy.is_dangerous(clean_query) or re.search(r'[;&|`$]', clean_query):
            logger.warning(f"[WindowsAutomation] Búsqueda bloqueada por patrón inseguro: {query}")
            return {
                "success": False,
                "count": 0,
                "items": [],
                "error_code": "BLOCKED_ACTION",
                "message": "Búsqueda bloqueada por contener comandos o patrones de riesgo no autorizados."
            }

        user_dirs = []
        if location:
            is_safe, custom_path, _ = SecurityPolicy.validate_path_access(location, must_exist=False)
            if is_safe and custom_path and custom_path.exists():
                user_dirs.append(custom_path)

        if not user_dirs:
            for d_name in ["Desktop", "Documents", "Downloads", "Pictures", "Music"]:
                d_path = SecurityPolicy.get_actual_user_dir(d_name)
                if d_path.exists():
                    user_dirs.append(d_path)

        matches = []
        for base_dir in user_dirs:
            try:
                for root, dirs, files in os.walk(str(base_dir)):
                    rel = os.path.relpath(root, str(base_dir))
                    if rel.count(os.sep) > 3:
                        dirs.clear()
                        continue

                    for f in files:
                        if f.startswith("."):
                            continue
                        if clean_query in f.lower():
                            f_path = Path(root) / f
                            matches.append({
                                "name": f,
                                "path": str(f_path),
                                "directory": str(Path(root)),
                                "is_dir": False,
                                "size_bytes": f_path.stat().st_size if f_path.exists() else 0
                            })
                            if len(matches) >= 5:
                                break
                    if len(matches) >= 5:
                        break
            except Exception:
                pass

        count = len(matches)
        if count == 0:
            return {
                "success": True,
                "count": 0,
                "items": [],
                "message": f"No encontré ningún archivo que coincida con '{query}' en tus carpetas autorizadas."
            }
        elif count == 1:
            item = matches[0]
            return {
                "success": True,
                "count": 1,
                "items": matches,
                "matched_path": item["path"],
                "message": f"Encontré: {item['name']} en {item['directory']}."
            }
        else:
            list_str = "\n".join([f"{i+1}. {m['name']} ({m['directory']})" for i, m in enumerate(matches)])
            return {
                "success": True,
                "count": count,
                "items": matches,
                "disambiguation_needed": True,
                "message": f"Encontré {count} archivos que coinciden con '{query}':\n{list_str}\n¿Cuál quieres abrir?"
            }

    @classmethod
    def open_url(cls, url: str) -> Dict[str, Any]:
        is_valid, clean_url, err = SecurityPolicy.validate_url(url)
        if not is_valid:
            return {"success": False, "error_code": err or "INVALID_URL", "message": "La dirección web especificada no es válida o segura."}

        try:
            webbrowser.open(clean_url)
            return {
                "success": True,
                "url": clean_url,
                "message": f"Abriendo {clean_url}."
            }
        except Exception as e:
            return {"success": False, "error_code": "EXECUTION_FAILED", "message": str(e)}

    @classmethod
    def open_file(cls, file_path: str) -> Dict[str, Any]:
        is_safe, safe_path, err = SecurityPolicy.validate_path_access(file_path, must_exist=True)
        if not is_safe or not safe_path:
            return {"success": False, "error_code": err or "INVALID_PATH", "message": f"No se puede acceder al archivo '{file_path}'."}

        if safe_path.is_dir():
            return cls.open_folder(str(safe_path))

        try:
            os.startfile(str(safe_path))
            return {
                "success": True,
                "path": str(safe_path),
                "message": f"Abriendo archivo {safe_path.name}."
            }
        except Exception as e:
            return {"success": False, "error_code": "EXECUTION_FAILED", "message": f"No se pudo abrir el archivo ({e})."}

    @classmethod
    def open_folder(cls, folder_path: str) -> Dict[str, Any]:
        is_safe, safe_path, err = SecurityPolicy.validate_path_access(folder_path, must_exist=False)
        if not is_safe or not safe_path:
            return {"success": False, "error_code": err or "INVALID_PATH", "message": f"Acceso denegado a la carpeta '{folder_path}'."}

        try:
            if not safe_path.exists():
                safe_path.mkdir(parents=True, exist_ok=True)
            subprocess.Popen(f'explorer.exe "{safe_path}"')
            return {
                "success": True,
                "path": str(safe_path),
                "message": f"Abriendo carpeta {safe_path.name}."
            }
        except Exception as e:
            return {"success": False, "error_code": "EXECUTION_FAILED", "message": f"No se pudo abrir la carpeta ({e})."}

    @classmethod
    def get_active_application(cls) -> Dict[str, Any]:
        try:
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return {"available": False, "title": None, "process": None, "pid": None}

            length = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            window_title = buf.value

            pid = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            proc_name = "Desconocido"
            try:
                p = psutil.Process(pid.value)
                proc_name = p.name()
            except Exception:
                pass

            canonical_key, app_info = ApplicationRegistry.resolve_app(proc_name)
            app_display = app_info["name"] if app_info else proc_name

            return {
                "available": True,
                "title": window_title,
                "process": proc_name,
                "app_name": app_display,
                "canonical_key": canonical_key,
                "pid": pid.value,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.debug(f"[WindowsAutomation] get_active_application falló: {e}")
            return {"available": False, "title": None, "process": None, "pid": None}

    @classmethod
    def set_volume(cls, level: Optional[int] = None, action: Optional[str] = None, delta: Optional[int] = None) -> Dict[str, Any]:
        """
        Ajusta el volumen del sistema Windows (0-100, mute/unmute, delta relativo) de forma no bloqueante.
        """
        try:
            user32 = ctypes.windll.user32
            VK_VOLUME_MUTE = 0xAD
            VK_VOLUME_DOWN = 0xAE
            VK_VOLUME_UP = 0xAF

            def _press(vk: int):
                user32.keybd_event(vk, 0, 0, 0)
                user32.keybd_event(vk, 0, 2, 0)

            act_clean = (action or "").lower().strip()
            if act_clean in ["mute", "silenciar"]:
                _press(VK_VOLUME_MUTE)
                logger.info("[WindowsAutomation] Volumen silenciado (mute).")
                return {
                    "success": True,
                    "status": "MUTED",
                    "action": "mute",
                    "message": "Audio del sistema silenciado."
                }

            if act_clean in ["unmute", "reactivar", "activar"]:
                _press(VK_VOLUME_MUTE)
                logger.info("[WindowsAutomation] Volumen reactivado (unmute).")
                return {
                    "success": True,
                    "status": "UNMUTED",
                    "action": "unmute",
                    "message": "Audio del sistema reactivado."
                }

            if delta is not None and level is None:
                steps = max(1, abs(round(delta / 2.0)))
                vk = VK_VOLUME_UP if delta > 0 else VK_VOLUME_DOWN
                for _ in range(steps):
                    _press(vk)
                direction = "subido" if delta > 0 else "bajado"
                logger.info(f"[WindowsAutomation] Volumen {direction} por delta: {delta}")
                return {
                    "success": True,
                    "status": "VOLUME_ADJUSTED",
                    "delta": delta,
                    "message": f"Volumen {direction} en aproximadamente {abs(delta)} puntos."
                }

            if level is not None:
                clamped = max(0, min(100, int(level)))
                # Reiniciar a 0 primero con 50 pasos de descenso
                for _ in range(50):
                    _press(VK_VOLUME_DOWN)
                steps = round(clamped / 2.0)
                for _ in range(steps):
                    _press(VK_VOLUME_UP)
                logger.info(f"[WindowsAutomation] Volumen ajustado a {clamped}%.")
                return {
                    "success": True,
                    "status": "VOLUME_SET",
                    "level": clamped,
                    "message": f"Volumen ajustado al {clamped}%."
                }

            return {
                "success": False,
                "status": "INVALID_ARGUMENTS",
                "error": "Debes especificar un nivel (0-100), delta (+/-) o acción (mute/unmute).",
                "message": "Por favor especifica el nivel deseado de volumen o la acción (ej. silenciar)."
            }
        except Exception as e:
            logger.error(f"[WindowsAutomation] Error en set_volume: {e}")
            return {
                "success": False,
                "status": "EXECUTION_FAILED",
                "error": str(e),
                "message": f"No se pudo ajustar el volumen: {e}"
            }

