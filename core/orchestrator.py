import re
import time
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from core.ai_provider import AIProvider
from core.config import settings
from core.logger import logger
from core.context_engine import ContextEngine
from core.memory_manager import memory_manager, MemoryType
from core.sentence_buffer import SentenceBuffer
from core.response_sanitizer import ResponseSanitizer
from core.document_generator import DocumentGenerator
from core.windows_automation import WindowsAutomationProvider
from core.security import SecurityPolicy, ActionRisk
from core.social_layer import SocialResponseLayer, ConversationState
from core.crisis_guard import CrisisSafetyGuard, CrisisRiskLevel, CrisisDecision
from core.relationship_manager import RelationshipManager
from core.platform_capabilities import PlatformCapabilities
from tools.router import ToolRouter

# Proveedores
from providers.gemini_provider import GeminiProvider
from providers.openrouter_provider import OpenRouterProvider
from providers.anthropic_provider import AnthropicProvider
from providers.mock_provider import MockAIProvider

# Herramientas del Sistema y Desktop
from tools.implementations.system_tools import CurrentDatetimeTool, LocationTool, ParseTimeTool, PingTool, SetVolumeTool
from tools.implementations.desktop_tools import (
    OpenAppTool, FocusAppTool, CloseAppTool, CloseWindowTool, SearchFilesTool, GetRunningAppsTool,
    OpenUrlTool, OpenFileTool, OpenFolderTool, ListFilesTool, GetActiveAppTool,
    CreateTextFileTool, ReadTextFileTool, CreatePdfTool, CreateDocxTool, GenerateImageTool,
    AnalyzeScreenTool
)
# Multimedia
from tools.implementations.music_tools import (
    PlayMusicTool, SearchMusicTool, PauseMusicTool, ResumeMusicTool, SkipMusicTool,
    GetNowPlayingTool, GetQueueTool, ClearQueueTool, RecommendMusicTool, SearchVideosTool
)
# Memoria
from tools.implementations.memory_tools import (
    RememberTool, RecallTool, ForgetMemoryTool, GetMemorySummaryTool, ClearMemoryTool, ExportMemoryTool
)
# Recordatorios y Tareas
from tools.implementations.reminder_tools import (
    CreateReminderTool, ListRemindersTool, SnoozeReminderTool, CompleteReminderTool,
    DeleteReminderTool, ClearRemindersTool, ClearAllPendingTool, PendingSummaryTool
)
from tools.implementations.task_tools import (
    CreateTaskTool, ListTasksTool, CompleteTaskTool, DeleteTaskTool, ClearTasksTool
)
from tools.implementations.web_tools import WebSearchTool, ReadWebpageTool, SearchYouTubeTool
from tools.implementations.automation_tools import ExecuteWorkflowTool, DailyBriefingTool

class JarvisOrchestrator:
    """
    Orquestador Central de JARVIS v3.0 con Arquitectura Multi-Provider,
    Fallback de IA en Cascada, Control de Herramientas y Memoria Contextual.
    """
    def __init__(self, primary_provider: Optional[AIProvider] = None):
        self.tool_router = ToolRouter()
        self._register_tools()
        self.crisis_guard = CrisisSafetyGuard()
        self.relationship_manager = RelationshipManager()

        # Cache del prompt de sistema adaptada por consulta (Roadmap Fase D)
        self._sysinstruction_cache: str = ""
        self._sysinstruction_cache_ts: float = 0.0
        self._last_cached_query: str = ""
        self._SYSINSTRUCTION_TTL: float = 20.0  # segundos

        # Construir lista de proveedores en orden de prioridad
        self.providers: List[AIProvider] = []
        if primary_provider:
            self.providers.append(primary_provider)
            self.mock_provider = primary_provider if isinstance(primary_provider, MockAIProvider) else MockAIProvider()
        else:
            # 1. Gemini (directo, ultra rápido)
            if settings.has_gemini_key:
                self.providers.append(GeminiProvider())

            # 2. OpenRouter (puerta de enlace multimodelo)
            if settings.has_openrouter_key:
                self.providers.append(OpenRouterProvider())

            # 3. Anthropic (directo)
            if settings.has_anthropic_key:
                self.providers.append(AnthropicProvider())

            # 4. Mock solo en modo desarrollo explícito
            self.mock_provider = MockAIProvider()
            if settings.DEV_MODE or not self.providers:
                self.providers.append(self.mock_provider)

        self.primary_provider = self.providers[0] if self.providers else self.mock_provider
        prov_names = [f"{p.name}({getattr(p, 'model_name', 'default')})" for p in self.providers]
        logger.info(f"[Orchestrator v3.0] Cadena de proveedores configurada: {' -> '.join(prov_names)}")

    def _register_tools(self):
        # Sistema
        self.tool_router.register_tool(CurrentDatetimeTool())
        self.tool_router.register_tool(LocationTool())
        self.tool_router.register_tool(ParseTimeTool())
        self.tool_router.register_tool(PingTool())
        self.tool_router.register_tool(SetVolumeTool())

        # Automatización de Windows / Desktop
        self.tool_router.register_tool(OpenAppTool())
        self.tool_router.register_tool(CloseAppTool())
        self.tool_router.register_tool(CloseWindowTool())
        self.tool_router.register_tool(SearchFilesTool())
        self.tool_router.register_tool(ListFilesTool())
        self.tool_router.register_tool(CreateTextFileTool())
        self.tool_router.register_tool(ReadTextFileTool())
        self.tool_router.register_tool(CreatePdfTool())
        self.tool_router.register_tool(CreateDocxTool())
        self.tool_router.register_tool(GenerateImageTool())

        # Herramientas exclusivas de Desktop (condicionadas a capacidades de plataforma B.3)
        if PlatformCapabilities.is_desktop():
            self.tool_router.register_tool(FocusAppTool())
            self.tool_router.register_tool(GetRunningAppsTool())
            self.tool_router.register_tool(OpenUrlTool())
            self.tool_router.register_tool(OpenFileTool())
            self.tool_router.register_tool(OpenFolderTool())
            self.tool_router.register_tool(GetActiveAppTool())
            self.tool_router.register_tool(AnalyzeScreenTool())

        # Multimedia
        self.tool_router.register_tool(PlayMusicTool())
        self.tool_router.register_tool(SearchMusicTool())
        self.tool_router.register_tool(PauseMusicTool())
        self.tool_router.register_tool(ResumeMusicTool())
        self.tool_router.register_tool(SkipMusicTool())
        self.tool_router.register_tool(GetNowPlayingTool())
        self.tool_router.register_tool(GetQueueTool())
        self.tool_router.register_tool(ClearQueueTool())
        self.tool_router.register_tool(RecommendMusicTool())
        self.tool_router.register_tool(SearchVideosTool())

        # Memoria
        self.tool_router.register_tool(RememberTool())
        self.tool_router.register_tool(RecallTool())
        self.tool_router.register_tool(ForgetMemoryTool())
        self.tool_router.register_tool(GetMemorySummaryTool())
        self.tool_router.register_tool(ExportMemoryTool())

        # Recordatorios y Tareas
        self.tool_router.register_tool(CreateReminderTool())
        self.tool_router.register_tool(ListRemindersTool())
        self.tool_router.register_tool(SnoozeReminderTool())
        self.tool_router.register_tool(CompleteReminderTool())
        self.tool_router.register_tool(PendingSummaryTool())
        self.tool_router.register_tool(ClearAllPendingTool())
        self.tool_router.register_tool(DeleteReminderTool())
        self.tool_router.register_tool(CreateTaskTool())
        self.tool_router.register_tool(ListTasksTool())
        self.tool_router.register_tool(CompleteTaskTool())
        self.tool_router.register_tool(DeleteTaskTool())

        # Web
        self.tool_router.register_tool(ReadWebpageTool())
        self.tool_router.register_tool(WebSearchTool())
        self.tool_router.register_tool(SearchYouTubeTool())

        # Automatización y Workflows Multi-paso (Fase 18)
        self.tool_router.register_tool(ExecuteWorkflowTool())
        self.tool_router.register_tool(DailyBriefingTool())

    def _get_provider_tools_schema(self, provider: AIProvider) -> List[Dict[str, Any]]:
        if provider.name == "anthropic":
            return self.tool_router.get_tools_schema_anthropic()
        # Gemini, OpenRouter y Mock aceptan schema tipo parameters/gemini
        return self.tool_router.get_tools_schema_gemini()

    def _build_system_instruction(self, current_user_query: str = "") -> str:
        """Construye el prompt de sistema con caché por consulta para evitar bloquear el event loop."""
        now = time.monotonic()
        if (
            self._sysinstruction_cache 
            and (now - self._sysinstruction_cache_ts) < self._SYSINSTRUCTION_TTL
            and self._last_cached_query == current_user_query
        ):
            return self._sysinstruction_cache

        profile = memory_manager.get_all_profile()
        all_personal = memory_manager.recall_memories(category="identidad", limit=20)
        contextual_mems = memory_manager.get_contextual_memories(current_user_query, limit=5)
        identity_keys = {m["key"] for m in all_personal}
        extra_mems = [m for m in contextual_mems if m["key"] not in identity_keys]
        recent_memories = all_personal + extra_mems

        tasks = memory_manager.list_tasks(include_completed=False)
        reminders = memory_manager.list_reminders(include_completed=False)

        context_block = ContextEngine.build_system_context_block(
            user_profile=profile,
            recent_memories=recent_memories,
            pending_tasks_count=len(tasks),
            active_reminders_count=len(reminders)
        )

        relational_block = self.relationship_manager.get_relational_prompt_block()
        personality_rules = memory_manager.user_profile.personality.to_instruction()

        instruction = f"""{context_block}

{relational_block}

Eres JARVIS, el asistente personal inteligente y compañero digital para Windows.
{personality_rules}

=== DIRECTIVAS ESTRICTAS DE COMPORTAMIENTO ===
1. CONVERSACIÓN NATURAL E INTELIGENTE:
   - Para saludos, preguntas de conocimiento general, historia, ciencia, programación, matemáticas, explicaciones o charla informal, responde DIRECTAMENTE con tu conocimiento sin llamar herramientas.
   - Mantén el contexto de la conversación previa.
   - Habla en español natural, conciso y fluido.
   - Usa el nombre del usuario (del perfil de contexto) cuando sea apropiado y natural.

2. APRENDIZAJE PROACTIVO Y PERMANENTE — REGLA CRÍTICA:
   - NUNCA llames `remember_info` para saludos ('hola', 'buenos días'), preguntas generales o charla ordinaria.
   - Cuando el usuario te comparta o mencione datos reales sobre sí mismo (nombre, edad, cumpleaños, gustos, familia, trabajo, hobbies, bandas favoritas, comidas, lugares, etc.), SIEMPRE llama `remember_info` INMEDIATAMENTE para guardar ese dato en memoria persistente.
   - Ejemplos que DEBEN disparar `remember_info`:
     * "Me llamo Juan" → key="nombre_completo", value="Juan"
     * "Mis amigos me llaman Dante" → key="alias", value="Dante"
     * "Tengo 25 años" → key="edad", value="25"
     * "Mi banda favorita es Metallica" → key="banda_favorita", value="Metallica"
     * "Trabajo de programador" → key="profesion", value="programador"
     * "Nací el 5 de mayo de 1999" → key="fecha_nacimiento", value="5 de mayo de 1999"
   - Para ALIAS y APODOS: guárdalos con key="alias" y también actualiza cómo te diriges al usuario.
     * Si el usuario tiene un alias guardado, ÚSALO para llamarle (ej. "Dante" en vez de "Jhonatan").
     * Si no tiene alias, usa su primer nombre del perfil.
   - Si el dato actualiza o contradice algo del perfil, actualiza el recuerdo existente.
   - Cuando el usuario te pida OLVIDAR algo, llama `forget_memory` inmediatamente.

3. USO ESTRICTO DE HERRAMIENTAS (SOLO CUANDO SE SOLICITE UNA ACCIÓN REAL):
   - Abre o cierra programas o aplicaciones → `open_application` / `close_application`
     * Soporta Opera, Opera GX, Chrome, Edge, Brave, Firefox, Calculadora, Bloc de notas, Explorador, VS Code, etc.
   - Cerrar ventanas o pestañas específicas → `close_window(window_title="...", app_name="...")` o `close_application(app_name="opera", window_title="...")`
     * Úsalo cuando el usuario pida cerrar una ventana o pestaña en particular (ej. "cierra la ventana de YouTube en Opera", "cierra la pestaña de GitHub", "cierra la ventana de X").
   - Abrir carpetas, escritorio o pestañas del explorador ("abre el escritorio", "abre pestañas del escritorio", "abre la carpeta descargas") → `open_folder(folder_path="desktop")` o `open_application(app_name="desktop")` o `open_application(app_name="explorer")`.
   - Buscar en YouTube ("busca en youtube...", "pon en youtube...", "quiero ver en youtube") → SIEMPRE llama a `search_youtube(query="...")`. NUNCA uses `open_url` con solo 'youtube.com' cuando hay una consulta de búsqueda.
   - Búsqueda web general en Google → `web_search(query="...")`
   - Crear archivos de texto simple → `create_text_file` (filename, content, location='desktop')
   - Crear documentos PDF formales (estilo APA/Calibri/Helvetica) → `create_pdf` (filename, title, content, standard='pdf/a', author='Dante', location='desktop').
     IMPORTANTE: `content` admite tablas Markdown ('| Col A | Col B |' + fila separadora '|---|---|') e imágenes ('![descripción](archivo.png)'). Si el usuario pide un documento con tabla o imagen, genera la imagen primero con `generate_image` si hace falta y luego incluye la sintaxis dentro de `content`. Se soportan rutas, URLs, base64 o auto-síntesis con máxima estrética APA. NUNCA digas que no puedes incluir imágenes en PDF o DOCX: sí puedes.
   - Crear documentos Word editables (.docx) → `create_docx` (filename, title, content, author='Dante', location='desktop'). Mismas reglas de tablas e imágenes que `create_pdf`.
   - Generar imágenes artísticas / fotográficas → `generate_image` (prompt, filename, location='pictures', style)
   - Leer archivos de texto → `read_text_file` (file_path)
   - Buscar o listar archivos → `search_files` / `list_files`
   - Música / Reproducción → `play_music` / `pause_music` / `resume_music` / `skip_music` / `recommend_music`
     * Peticiones musicales con adjetivos o tonos (ej. "pon la canción más triste de Billie", "canción melancólica", "música triste") → SIEMPRE llama a `play_music(song_name="...")` (ej. "Billie Eilish What Was I Made For" o "Billie Eilish when the party's over"). NUNCA confundas solicitudes musicales con crisis emocionales.
     * Identificación de artistas e instrumentos: Respeta estrictamente el género gramatical y descripción dada por el usuario (ej. si dice "un chico que canta con violín" o "un chico con un solo de violín", refiere a intérpretes masculinos como Alexander Rybak — 'Fairytale', David Garrett, Bryson Andres, o Yellowcard, NUNCA a intérpretes femeninas como Lindsey Stirling).
   - Borrar la cola de música (\"borra la lista\", \"limpia la cola\", \"para todo\") → `clear_music_queue`
   - Recordatorios y pendientes:
     * Crear recordatorio → `create_reminder`
     * Consultar pendientes o qué tengo que hacer → `get_pending_summary`
     * Borrar/eliminar TODOS los pendientes, recordatorios o tareas ("borra eso", "borra los recordatorios", "limpia mis pendientes") → `clear_all_pending`
     * Borrar un recordatorio específico → `delete_reminder`
     * Borrar una tarea específica → `delete_task`
     * Crear tarea → `create_task`
     * Completar tarea → `complete_task`
   - Guardar memoria ("Recuerda que...", "Mi X favorito es Y") → `remember_info`
   - Olvidar memoria ("Olvida que...", "Borra el recuerdo de...") → `forget_memory`
   - Consultar qué recuerdas ("¿Qué recuerdas sobre X?") → `recall_memories`
   - Subir/bajar/silenciar volumen → `set_volume` (level 0-100, o delta=-10/+10, o action="mute"/"unmute")
   - NUNCA intentes borrar o eliminar archivos del sistema.

4. HONESTIDAD Y PENSAMIENTO CRÍTICO — REGLA OBLIGATORIA:
   - Si el usuario dice algo incorrecto o discutible, SEÑÁLALO con respeto y argumentación clara. No des la razón por default.
   - Si una idea tiene riesgos reales (técnicos, económicos, personales), menciónalos aunque el usuario parezca entusiasmado.
   - Si no estás seguro de algo, DILO directamente: "No tengo certeza sobre eso" o "Habría que verificarlo".
   - Nunca halagues una idea solo para complacer. La honestidad útil es más valiosa que el acuerdo vacío.
   - Puedes disentir: "En realidad creo que..." o "De hecho, ese enfoque tiene una trampa:" son formas válidas de responder.

5. NUNCA inventes herramientas ni llames herramientas para conversación ordinaria.
"""

        self._sysinstruction_cache = instruction
        self._sysinstruction_cache_ts = now
        self._last_cached_query = current_user_query
        return instruction

    def invalidate_sysinstruction_cache(self):
        """Forzar re-generación del prompt en el próximo mensaje (e.g. después de guardar memoria)."""
        self._sysinstruction_cache_ts = 0.0
        self._last_cached_query = ""


    def _format_spoken_tool_phrase(self, tool_name: str, tool_args: Dict[str, Any], tool_result: Dict[str, Any]) -> str:
        return SocialResponseLayer.format_social_tool_phrase(
            tool_name=tool_name,
            tool_args=tool_args,
            tool_result=tool_result,
            personality=memory_manager.user_profile.personality
        )

    def _resolve_contextual_anaphora(self, user_text: str) -> str:
        low = user_text.lower().strip()
        if any(ph in low for ph in ["cierra eso", "ciérralo", "cierralo", "cierra esta app", "cierra la ventana actual"]):
            active_info = WindowsAutomationProvider.get_active_application()
            if active_info.get("available") and active_info.get("canonical_key"):
                app_key = active_info["canonical_key"]
                logger.info(f"[Orchestrator] Anáfora resuelta: 'cierra eso' -> close_application('{app_key}')")
                return f"cierra {app_key}"
        return user_text

    def _handle_style_feedback(self, prompt: str) -> Optional[str]:
        low = prompt.lower().strip()
        reply = None
        if low in ["háblame más corto", "hablame mas corto", "más breve", "mas breve", "más corto", "mas corto"]:
            memory_manager.user_profile.personality.adjust_style("corto")
            memory_manager.store_memory("estilo_comunicacion", "Prefiere respuestas ultra cortas", mem_type=MemoryType.SYSTEM_PREFERENCE)
            reply = "Entendido, seré más directo."
        elif low in ["háblame más divertido", "hablame mas divertido", "más divertido", "mas divertido", "sé más gracioso", "se mas gracioso"]:
            memory_manager.user_profile.personality.adjust_style("divertido")
            memory_manager.store_memory("estilo_humor", "Prefiere tono más divertido", mem_type=MemoryType.SYSTEM_PREFERENCE)
            reply = "De acuerdo, le pondré más chispa al asunto."
        elif low in ["deja de hacer bromas", "más serio", "mas serio", "modo serio"]:
            memory_manager.user_profile.personality.adjust_style("serio")
            memory_manager.store_memory("estilo_humor", "Prefiere tono serio", mem_type=MemoryType.SYSTEM_PREFERENCE)
            reply = "Comprendido. Modo sobrio y profesional activado."
        elif low in ["muy robótico", "muy robotico", "más natural", "mas natural"]:
            memory_manager.user_profile.personality.adjust_style("natural")
            reply = "Tomado en cuenta, hablaré con más soltura."
        elif low in ["eso estuvo bien", "me gustó esa respuesta", "me gusto esa respuesta"]:
            reply = "Me alegra que te haya gustado."

        if reply:
            self.relationship_manager.sync_personality_profile(memory_manager.user_profile.personality)
            self.invalidate_sysinstruction_cache()
            self.relationship_manager.record_turn(prompt=prompt, response_text=reply)
        return reply


    @classmethod
    def _persist_incoming_image(cls, image_data: Optional[Dict[str, Any]]) -> Optional[str]:
        if not image_data or not image_data.get("data"):
            return None
        try:
            import base64
            b64_str = image_data["raw_data"] if "raw_data" in image_data else image_data["data"]
            raw_bytes = base64.b64decode(b64_str)
            pics_dir = SecurityPolicy.get_actual_user_dir("Pictures")
            pics_dir.mkdir(parents=True, exist_ok=True)
            saved_path = pics_dir / f"jarvis_chat_adjunto_{int(time.time())}.png"
            with open(saved_path, "wb") as f:
                f.write(raw_bytes)
            DocumentGenerator.set_last_session_image(saved_path)
            logger.info(f"[Orchestrator] Imagen entrante persistida en: {saved_path}")
            return str(saved_path)
        except Exception as ex:
            logger.warning(f"[Orchestrator] Error persistiendo imagen entrante: {ex}")
            return None


    async def _auto_generate_pdf_with_image_if_requested(
        self,
        clean_prompt: str,
        executed_tools: List[Dict[str, Any]],
        image_result: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        low_p = clean_prompt.lower()
        if not any(k in low_p for k in ["pdf", "documento"]):
            return None
        if any(t.get("tool_name") in ["create_pdf", "create_docx"] for t in executed_tools):
            return None

        logger.info("[Orchestrator Safeguard] Solicitud de PDF con imágenes detectada. Creando PDF automáticamente...")
        img_data = image_result.get("data", {})
        img_path = img_data.get("path") or img_data.get("file_name") or "imagen.png"
        img_prompt = img_data.get("prompt") or "Referencia Visual"

        raw_topic = re.sub(r'(?i)(quiero que hagas|haz|crea|genera|un|el|la|de los|de las|del|de|sobre|un documento|un pdf|pdf)\s+', ' ', clean_prompt)
        parts = re.split(r'(?i)\s+(y agregues|con referencias|con imágenes|con imagenes|con fotos|con una imagen|y ponle)', raw_topic)
        topic_part = parts[0].strip()
        topic = topic_part.title() if topic_part and len(topic_part) > 2 else "Investigación Técnica"

        doc_filename = f"{re.sub(r'[^a-zA-Z0-9]', '_', topic[:25]).lower()}_{int(time.time())}.pdf"
        doc_title = f"{topic}: Informe Técnico y Referencias Visuales"
        doc_content = f"""# {topic}

Este documento formal ha sido estructurado bajo estándares de investigación y maquetación APA, compilando los fundamentos teóricos y el análisis visual correspondiente.

## 1. Referencia Visual Estructurada

A continuación se presenta la figura técnica ilustrativa del tema de estudio:

![{img_prompt}]({img_path})

## 2. Fundamentos y Principios Técnicos

- **Origen y Funcionamiento:** Análisis detallado de las propiedades físicas y operativas de {topic}.
- **Arquitectura y Componentes:** Elementos críticos representados en la figura técnica anterior.
- **Aplicaciones y Relevancia:** Importancia histórica e industrial en los sistemas modernos y la ingeniería.

## 3. Conclusiones

La integración de referencias visuales normalizadas permite una comprensión integral y rigurosa de la materia analizada.
"""
        pdf_res = await self.tool_router.execute_tool("create_pdf", {
            "filename": doc_filename,
            "title": doc_title,
            "content": doc_content,
            "standard": "pdf/a",
            "author": memory_manager.user_profile.name or "Dante",
            "location": "desktop"
        })
        return pdf_res

    async def process_user_input(
        self,
        user_text: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        image_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        clean_prompt = user_text.strip()
        if not clean_prompt and not image_data:
            return {"success": False, "response_text": "Por favor ingresa un mensaje.", "tools_executed": []}

        logger.info(f"[INPUT] User: '{clean_prompt}' (Image: {bool(image_data)})")

        # Feedback de personalidad directo
        feedback_reply = self._handle_style_feedback(clean_prompt)
        if feedback_reply:
            return {
                "success": True,
                "response_text": feedback_reply,
                "tools_executed": [],
                "action_type": "social_feedback",
                "action_detail": "Ajuste de personalidad"
            }

        # Seguridad
        low_p = clean_prompt.lower()
        if any(w in low_p for w in ["system32", "rm -rf", "del /f", "format c:"]) or (SecurityPolicy.is_dangerous(clean_prompt) and "carpeta" not in low_p):
            msg = "Esta acción compromete la integridad del sistema y ha sido bloqueada por seguridad."
            return {
                "success": True,
                "response_text": msg,
                "tools_executed": [],
                "action_type": "security_blocked",
                "action_detail": "Acción bloqueada"
            }

        if any(w in low_p for w in ["elimina esta carpeta", "borra esta carpeta", "formatea", "apaga el pc", "apagar el computador"]):
            msg = "Esta acción es potencialmente destructiva. Por favor confirma si estás seguro de que deseas proceder."
            return {
                "success": True,
                "response_text": msg,
                "tools_executed": [],
                "action_type": "security_confirmation",
                "action_detail": "Confirmación requerida"
            }

        # Guardián de seguridad relacional y contención de crisis (Roadmap Fase D)
        crisis_decision = await self.crisis_guard.evaluate_message(clean_prompt, self.primary_provider)
        if crisis_decision.is_interruptive and crisis_decision.response_text:
            return {
                "success": True,
                "response_text": crisis_decision.response_text,
                "tools_executed": [],
                "action_type": "crisis_guard_interrupt",
                "action_detail": f"Intervención de seguridad ({crisis_decision.risk_level.value})"
            }

        clean_prompt = self._resolve_contextual_anaphora(clean_prompt)
        self._persist_incoming_image(image_data)

        # Historial multi-turn
        history = conversation_history or []
        messages = []
        for h in history[-8:]:
            role = "user" if h.get("role") in ["user", "human"] else "assistant"
            messages.append({"role": role, "content": h.get("content", "")})
        user_msg = {"role": "user", "content": clean_prompt}
        if image_data:
            user_msg["image"] = image_data
        messages.append(user_msg)

        system_prompt = self._build_system_instruction(current_user_query=clean_prompt)

        # Ejecutar llamada con la cadena de fallback
        ai_response = None
        for prov in self.providers:
            schema = self._get_provider_tools_schema(prov)
            logger.info(f"[LLM REQUEST] Intentando proveedor: {prov.name} ({getattr(prov, 'model_name', 'default')})")
            try:
                ai_response = await prov.generate_response(
                    messages=messages,
                    system_prompt=system_prompt,
                    tools=schema
                )
                if ai_response.get("success"):
                    break
                else:
                    logger.warning(f"[Orchestrator] Proveedor {prov.name} falló: {ai_response.get('error')}. Probando siguiente en cascada...")
            except Exception as ex:
                logger.warning(f"[Orchestrator] Excepción en {prov.name}: {ex}. Probando siguiente en cascada...")

        # Si todos los proveedores fallan y no estamos en DEV_MODE
        if not ai_response or not ai_response.get("success"):
            error_msg = "No puedo conectarme a ningún proveedor de IA en este momento. Por favor verifica tus credenciales o conexión."
            logger.error(f"[Orchestrator] Fallaron todos los proveedores de IA configurados.")
            return {
                "success": False,
                "response_text": error_msg,
                "tools_executed": [],
                "error": "ALL_PROVIDERS_FAILED",
                "provider": "none"
            }

        executed_tools = []
        playlist = None
        current_track = None
        tracks = []
        action_type = None
        action_detail = None
        tool_spoken_phrase = None
        generated_image = None
        generated_doc = None

        for call in ai_response.get("tool_calls", []):
            t_name = call["name"]
            t_args = call.get("input", {})
            logger.info(f"[TOOL CALL] {t_name} with args: {t_args}")
            
            if t_name == "create_reminder" and "priority" not in t_args:
                prompt_low = clean_prompt.lower()
                urgent_kw = ["urgente", "urgentísimo", "urgentisimo", "importantísima", "importantisima", "critico", "crítico", "no puedo llegar tarde"]
                high_kw = ["importante", "alta prioridad", "reunión", "reunion", "clave"]
                if any(w in prompt_low for w in urgent_kw):
                    t_args["priority"] = "URGENT"
                elif any(w in prompt_low for w in high_kw):
                    t_args["priority"] = "HIGH"
                else:
                    t_args["priority"] = "NORMAL"

            t_result = await self.tool_router.execute_tool(t_name, t_args)
            logger.info(f"[TOOL RESULT] {t_name} -> {t_result.get('success')}")
            executed_tools.append({"tool_name": t_name, "result": t_result})
            tool_spoken_phrase = self._format_spoken_tool_phrase(t_name, t_args, t_result)

            if t_result.get("success") and t_name in ["remember_info", "forget_memory", "create_reminder", "delete_reminder", "clear_all_pending", "create_task", "complete_task", "delete_task"]:
                self.invalidate_sysinstruction_cache()

            if t_result.get("success") and t_result.get("data", {}).get("playlist"):
                playlist = t_result["data"]["playlist"]
                current_track = t_result["data"].get("current_track")
                tracks = t_result["data"].get("tracks", [])
                action_type = "music"
                action_detail = f"{len(playlist)} canciones en cola"
            elif t_result.get("success") and t_name == "clear_music_queue":
                playlist = []
                current_track = None
                tracks = []
                action_type = "music"
                action_detail = "Cola vaciada"
            elif t_result.get("success") and t_name == "open_application":
                action_type = "windows"
                action_detail = f"Abriendo {t_args.get('app_name', 'app')}"
            elif t_result.get("success") and t_name == "generate_image":
                action_type = "image"
                action_detail = "Imagen generada"
                generated_image = t_result.get("data", {}).get("data_url")
            elif t_result.get("success") and t_name in ["create_pdf", "create_docx"]:
                action_type = "document"
                action_detail = f"Documento {t_result.get('data', {}).get('format', 'PDF')} creado"
                generated_doc = t_result.get("data")

                # Safeguard para solicitudes de PDF con imagen
        if any(t.get("tool_name") == "generate_image" for t in executed_tools):
            img_rec = next((t["result"] for t in executed_tools if t.get("tool_name") == "generate_image"), None)
            if img_rec and img_rec.get("success"):
                pdf_res = await self._auto_generate_pdf_with_image_if_requested(clean_prompt, executed_tools, img_rec)
                if pdf_res and pdf_res.get("success"):
                    executed_tools.append({"tool_name": "create_pdf", "result": pdf_res})
                    action_type = "document"
                    action_detail = f"PDF '{pdf_res.get('data', {}).get('file_name')}' creado con imágenes"
                    generated_doc = pdf_res.get("data")
                    tool_spoken_phrase = f"He generado el documento PDF '{pdf_res.get('data', {}).get('file_name')}' con la referencia visual en tu Escritorio."

        final_raw_text = tool_spoken_phrase or ai_response.get("text", "")
        clean_user_text = ResponseSanitizer.sanitize(final_raw_text, user_name=memory_manager.user_profile.name)
        if not clean_user_text:
            clean_user_text = "Entendido."

        logger.info(f"[FINAL RESPONSE] '{clean_user_text}' (Provider: {ai_response.get('provider')}, Tools: {len(executed_tools)})")

        # Registro relacional multiturno (Roadmap Fase D.4)
        try:
            self.relationship_manager.record_turn(
                prompt=clean_prompt,
                response_text=clean_user_text,
                has_tools=bool(executed_tools)
            )
        except Exception as _rel_ex:
            logger.warning(f"[Orchestrator] RelationshipManager.record_turn falló silenciosamente: {_rel_ex}")

        return {
            "success": True,
            "response_text": clean_user_text,
            "tools_executed": executed_tools,
            "playlist": playlist,
            "current_track": current_track,
            "tracks": tracks,
            "action_type": action_type,
            "action_detail": action_detail,
            "generated_image": generated_image,
            "generated_doc": generated_doc,
            "provider": ai_response.get("provider", "unknown")
        }

    async def process_user_input_stream(
        self, 
        user_text: str, 
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        image_data: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        clean_prompt = user_text.strip()
        if not clean_prompt and not image_data:
            yield {"type": "sentence", "text": "Por favor ingresa un mensaje.", "is_final": True}
            return

        feedback_reply = self._handle_style_feedback(clean_prompt)
        if feedback_reply:
            yield {"type": "sentence", "text": feedback_reply, "is_final": True}
            yield {"type": "response_end", "full_text": feedback_reply, "tools_executed": []}
            return

        low_p = clean_prompt.lower()
        if any(w in low_p for w in ["system32", "rm -rf", "del /f", "format c:"]) or (SecurityPolicy.is_dangerous(clean_prompt) and "carpeta" not in low_p):
            msg = "Esta acción compromete la integridad del sistema y ha sido bloqueada por seguridad."
            yield {"type": "sentence", "text": msg, "is_final": True}
            yield {"type": "response_end", "full_text": msg, "tools_executed": []}
            return

        if any(w in low_p for w in ["elimina esta carpeta", "borra esta carpeta", "formatea", "apaga el pc", "apagar el computador"]):
            msg = "Esta acción es potencialmente destructiva. Por favor confirma si deseas proceder."
            yield {"type": "sentence", "text": msg, "is_final": True}
            yield {"type": "response_end", "full_text": msg, "tools_executed": []}
            return

        # Guardián de seguridad relacional y contención de crisis (Roadmap Fase D)
        crisis_decision = await self.crisis_guard.evaluate_message(clean_prompt, self.primary_provider)
        if crisis_decision.is_interruptive and crisis_decision.response_text:
            yield {"type": "sentence", "text": crisis_decision.response_text, "is_final": True}
            yield {
                "type": "response_end",
                "full_text": crisis_decision.response_text,
                "tools_executed": [],
                "action_type": "crisis_guard_interrupt",
                "action_detail": f"Intervención de seguridad ({crisis_decision.risk_level.value})"
            }
            return

        clean_prompt = self._resolve_contextual_anaphora(clean_prompt)
        self._persist_incoming_image(image_data)

        history = conversation_history or []
        messages = []
        for h in history[-8:]:
            role = "user" if h.get("role") in ["user", "human"] else "assistant"
            messages.append({"role": role, "content": h.get("content", "")})
        user_msg = {"role": "user", "content": clean_prompt}
        if image_data:
            user_msg["image"] = image_data
        messages.append(user_msg)

        system_prompt = self._build_system_instruction(current_user_query=clean_prompt)
        buffer = SentenceBuffer()
        accumulated_llm_text = ""
        tool_calls = []
        stream_successful = False

        # Intentar stream a través de la cadena de proveedores
        for prov in self.providers:
            schema = self._get_provider_tools_schema(prov)
            try:
                got_any = False
                async for chunk in prov.generate_response_stream(
                    messages=messages,
                    system_prompt=system_prompt,
                    tools=schema
                ):
                    if chunk.get("type") == "error":
                        logger.warning(f"[Orchestrator Stream] Error en {prov.name}: {chunk.get('error')}")
                        break
                    
                    got_any = True
                    if chunk.get("type") == "token":
                        token = chunk.get("content", "")
                        accumulated_llm_text += token
                        # Emisión inmediata token por token hacia el cliente (baja latencia visual)
                        yield {"type": "token", "content": token}
                        ready_phrases = buffer.add_token(token)
                        for p in ready_phrases:
                            clean_p = ResponseSanitizer.sanitize(p, user_name=memory_manager.user_profile.name)
                            if clean_p:
                                yield {"type": "sentence", "text": clean_p, "is_final": False}
                    elif chunk.get("type") == "tool_call":
                        tool_calls.append(chunk["tool_call"])

                if got_any:
                    stream_successful = True
                    break
            except Exception as ex:
                logger.warning(f"[Orchestrator Stream] Excepción en {prov.name} ({ex}). Probando siguiente...")

        if not stream_successful:
            error_msg = "No puedo conectarme a ningún proveedor de IA en este momento. Por favor verifica tus credenciales o conexión."
            yield {"type": "sentence", "text": error_msg, "is_final": True}
            yield {"type": "response_end", "full_text": error_msg, "tools_executed": []}
            return

        tool_executed_records = []
        tool_spoken_phrases = []
        generated_image = None
        generated_doc = None

        if tool_calls:
            for tc in tool_calls:
                t_name = tc["name"]
                t_args = tc.get("input", {})
                
                if t_name == "create_reminder" and "priority" not in t_args:
                    prompt_low = clean_prompt.lower()
                    urgent_kw = ["urgente", "urgentísimo", "urgentisimo", "importantísima", "importantisima", "critico", "crítico", "no puedo llegar tarde"]
                    high_kw = ["importante", "alta prioridad", "reunión", "reunion", "clave"]
                    if any(w in prompt_low for w in urgent_kw):
                        t_args["priority"] = "URGENT"
                    elif any(w in prompt_low for w in high_kw):
                        t_args["priority"] = "HIGH"
                    else:
                        t_args["priority"] = "NORMAL"

                t_res = await self.tool_router.execute_tool(t_name, t_args)
                if t_res.get("success") and t_name in ["remember_info", "forget_memory", "create_reminder", "delete_reminder", "clear_all_pending", "create_task", "complete_task", "delete_task"]:
                    self.invalidate_sysinstruction_cache()

                spoken_phrase = self._format_spoken_tool_phrase(t_name, t_args, t_res)
                clean_spoken = ResponseSanitizer.sanitize(spoken_phrase, user_name=memory_manager.user_profile.name)
                
                if t_res.get("success") and t_name == "generate_image":
                    generated_image = t_res.get("data", {}).get("data_url")
                elif t_res.get("success") and t_name in ["create_pdf", "create_docx"]:
                    generated_doc = t_res.get("data")

                tool_record = {"tool_name": t_name, "result": t_res, "spoken_phrase": clean_spoken}
                tool_executed_records.append(tool_record)
                tool_spoken_phrases.append(clean_spoken)
                
                yield {"type": "tool_executed", "tool_name": t_name, "result": t_res}
                yield {"type": "sentence", "text": clean_spoken, "is_final": False}
            if any(t.get("tool_name") == "generate_image" for t in tool_executed_records):
                img_rec = next((t["result"] for t in tool_executed_records if t.get("tool_name") == "generate_image"), None)
                if img_rec and img_rec.get("success"):
                    pdf_res = await self._auto_generate_pdf_with_image_if_requested(clean_prompt, tool_executed_records, img_rec)
                    if pdf_res and pdf_res.get("success"):
                        clean_spoken = f"He generado el documento PDF '{pdf_res.get('data', {}).get('file_name')}' con la referencia visual en tu Escritorio."
                        tool_record = {"tool_name": "create_pdf", "result": pdf_res, "spoken_phrase": clean_spoken}
                        tool_executed_records.append(tool_record)
                        tool_spoken_phrases.append(clean_spoken)
                        generated_doc = pdf_res.get("data")
                        yield {"type": "tool_executed", "tool_name": "create_pdf", "result": pdf_res}
                        yield {"type": "sentence", "text": clean_spoken, "is_final": False}

        final_chunks = buffer.flush()
        for fc in final_chunks:
            clean_fc = ResponseSanitizer.sanitize(fc, user_name=memory_manager.user_profile.name)
            if clean_fc:
                yield {"type": "sentence", "text": clean_fc, "is_final": False}

        # Construir texto final consolidado (preservando texto LLM y texto de tools sin sobreescribir destructivamente BUG-13)
        parts = []
        if tool_spoken_phrases:
            unique_phrases = []
            for p in tool_spoken_phrases:
                if p not in unique_phrases:
                    unique_phrases.append(p)
            parts.extend(unique_phrases)
        elif accumulated_llm_text:
            parts.append(accumulated_llm_text)

        consolidated_text = " ".join(parts) if parts else "Entendido."
        clean_final = ResponseSanitizer.sanitize(consolidated_text, user_name=memory_manager.user_profile.name)
        if not clean_final:
            clean_final = "Entendido."

        # Registro relacional multiturno (Roadmap Fase D.4)
        try:
            self.relationship_manager.record_turn(
                prompt=clean_prompt,
                response_text=clean_final,
                has_tools=bool(tool_executed_records)
            )
        except Exception as _rel_ex:
            logger.warning(f"[Orchestrator Stream] RelationshipManager.record_turn falló silenciosamente: {_rel_ex}")

        yield {
            "type": "response_end",
            "full_text": clean_final,
            "tools_executed": tool_executed_records,
            "generated_image": generated_image,
            "generated_doc": generated_doc
        }
