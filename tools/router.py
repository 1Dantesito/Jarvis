from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
from core.logger import logger
from core.security import SecurityPolicy, ActionRisk
from core.platform_capabilities import PlatformCapabilities

class ToolType(str, Enum):
    ACTION = "action"   # Muta estado del sistema/reproductor/archivos/BD
    QUERY = "query"     # Solo consulta/lee datos sin mutar estado

class BaseTool(ABC):
    name: str
    description: str
    tool_type: ToolType = ToolType.ACTION
    parameters_schema: Dict[str, Any]

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Retorna:
        {
            "success": bool,
            "data": Dict[str, Any],
            "error": Optional[str]
        }
        """
        pass

# Registro estricto de clasificación de todas las herramientas (BUG-24)
TOOL_REGISTRY: Dict[str, ToolType] = {
    # Sistema
    "get_current_datetime": ToolType.QUERY,
    "current_datetime": ToolType.QUERY,
    "get_location": ToolType.QUERY,
    "parse_relative_time": ToolType.QUERY,
    "parse_time": ToolType.QUERY,
    "ping": ToolType.QUERY,

    # Desktop y Automatización de Windows
    "open_application": ToolType.ACTION,
    "focus_application": ToolType.ACTION,
    "close_application": ToolType.ACTION,
    "close_window": ToolType.ACTION,
    "search_files": ToolType.QUERY,
    "get_running_applications": ToolType.QUERY,
    "open_url": ToolType.ACTION,
    "open_file": ToolType.ACTION,
    "open_folder": ToolType.ACTION,
    "list_files": ToolType.QUERY,
    "get_active_application": ToolType.QUERY,
    "create_text_file": ToolType.ACTION,
    "read_text_file": ToolType.QUERY,
    "create_pdf": ToolType.ACTION,
    "create_docx": ToolType.ACTION,
    "generate_image": ToolType.ACTION,
    "analyze_screen": ToolType.QUERY,

    # Multimedia / Música
    "play_music": ToolType.ACTION,
    "search_music": ToolType.QUERY,
    "pause_music": ToolType.ACTION,
    "resume_music": ToolType.ACTION,
    "skip_music": ToolType.ACTION,
    "get_now_playing": ToolType.QUERY,
    "get_music_queue": ToolType.QUERY,
    "clear_music_queue": ToolType.ACTION,
    "recommend_music": ToolType.ACTION,
    "search_videos": ToolType.QUERY,

    # Memoria
    "remember_info": ToolType.ACTION,
    "recall_memories": ToolType.QUERY,
    "forget_memory": ToolType.ACTION,
    "get_memory_summary": ToolType.QUERY,
    "clear_memory": ToolType.ACTION,
    "export_memory": ToolType.QUERY,

    # Recordatorios y Tareas
    "create_reminder": ToolType.ACTION,
    "list_reminders": ToolType.QUERY,
    "snooze_reminder": ToolType.ACTION,
    "complete_reminder": ToolType.ACTION,
    "delete_reminder": ToolType.ACTION,
    "clear_all_reminders": ToolType.ACTION,
    "clear_all_pending": ToolType.ACTION,
    "get_pending_summary": ToolType.QUERY,
    "create_task": ToolType.ACTION,
    "list_tasks": ToolType.QUERY,
    "complete_task": ToolType.ACTION,
    "delete_task": ToolType.ACTION,
    "clear_all_tasks": ToolType.ACTION,

    # Web
    "read_webpage": ToolType.QUERY,
    "web_search": ToolType.ACTION,
    "search_youtube": ToolType.ACTION,

    # Control de sistema
    "set_volume": ToolType.ACTION,

    # Automatización y Workflows Multi-paso (Fase 18)
    "execute_workflow": ToolType.ACTION,
    "get_daily_briefing": ToolType.QUERY,

    # Cisco Packet Tracer & Redes
    "solve_telematica_lab": ToolType.ACTION,
    "generate_packet_tracer_pkt": ToolType.ACTION,
}

class ToolRouter:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register_tool(self, tool: BaseTool):
        # Validación Fail-Fast de clasificación de tool (BUG-24)
        if tool.name not in TOOL_REGISTRY:
            raise ValueError(f"[ToolRouter] ERROR FATAL: La herramienta '{tool.name}' no está clasificada en TOOL_REGISTRY.")
        
        tool.tool_type = TOOL_REGISTRY[tool.name]
        if hasattr(tool, "set_router"):
            tool.set_router(self)
        self._tools[tool.name] = tool
        logger.debug(f"[ToolRouter] Herramienta registrada: {tool.name} (Tipo: {tool.tool_type.value})")

    def get_tool_type(self, tool_name: str) -> ToolType:
        return TOOL_REGISTRY.get(tool_name, ToolType.ACTION)

    def get_tools_schema_anthropic(self) -> List[Dict[str, Any]]:
        schemas = []
        for tool in self._tools.values():
            schemas.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.parameters_schema
            })
        return schemas

    def get_tools_schema_gemini(self) -> List[Dict[str, Any]]:
        schemas = []
        for tool in self._tools.values():
            schemas.append({
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters_schema
            })
        return schemas

    def get_tools_schema_openai(self) -> List[Dict[str, Any]]:
        """
        Retorna esquemas de Function Calling en el formato estándar de OpenAI / OpenRouter.
        """
        schemas = []
        for tool in self._tools.values():
            schemas.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters_schema
                }
            })
        return schemas

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Extraer objetivo/argumentos clave para inspección de seguridad
        target = ""
        for key in ("target", "file_path", "filename", "app_name", "query", "url", "command", "location", "folder_path"):
            if key in arguments and isinstance(arguments[key], str):
                target = arguments[key]
                break
        if not target and arguments:
            target = " ".join(str(v) for v in arguments.values() if isinstance(v, (str, int, float)))

        # 2. Filtrado estricto con SecurityPolicy (ALLOWLIST / Fail-Closed)
        risk = SecurityPolicy.classify_action(tool_name, target)
        if risk == ActionRisk.BLOCKED:
            logger.warning(f"[ToolRouter] Acción interceptada y bloqueada por SecurityPolicy: {tool_name} (target: '{target}')")
            return {
                "success": False,
                "data": {},
                "error": f"Acción bloqueada por política de seguridad (ALLOWLIST): {tool_name}"
            }
        elif risk == ActionRisk.CONFIRMATION_REQUIRED:
            logger.warning(f"[ToolRouter] Acción requiere confirmación previa: {tool_name}")
            return {
                "success": False,
                "data": {"confirmation_required": True, "tool_name": tool_name, "arguments": arguments},
                "error": f"Esta acción requiere confirmación explícita del usuario: {tool_name}"
            }

        # 2b. Filtrado estricto por capa de capacidades de plataforma (Fase B.3)
        is_supported, platform_error = PlatformCapabilities.is_tool_supported(tool_name)
        if not is_supported:
            logger.warning(f"[ToolRouter] Acción interceptada por capacidades de plataforma: {tool_name}")
            return {
                "success": False,
                "data": {"platform_restricted": True, "required_platform": "desktop"},
                "error": platform_error
            }

        # 3. Comprobar existencia en catálogo de herramientas
        if tool_name not in self._tools:
            return {
                "success": False,
                "data": {},
                "error": f"Herramienta no registrada: {tool_name}"
            }

        # 4. Ejecución segura de la herramienta
        try:
            result = await self._tools[tool_name].execute(**arguments)
            return result
        except Exception as e:
            logger.error(f"[ToolRouter] Error ejecutando {tool_name}: {e}")
            return {
                "success": False,
                "data": {},
                "error": str(e)
            }

