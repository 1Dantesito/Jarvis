import asyncio
from typing import Dict, Any
from tools.router import BaseTool
from core.context_engine import ContextEngine
from core.time_parser import TimeParser
from core.location_provider import LocationProvider
from core.windows_automation import WindowsAutomationProvider
from core.permissions import PermissionManager, PermissionCategory

class CurrentDatetimeTool(BaseTool):
    name = "get_current_datetime"
    description = "Obtiene la fecha, hora exacta en vivo, día de la semana, zona horaria y offset UTC del sistema."
    parameters_schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        data = ContextEngine.get_current_datetime_dict()
        return {
            "success": True,
            "data": data,
            "error": None
        }

class LocationTool(BaseTool):
    name = "get_location"
    description = "Consulta la ubicación geográfica actual (ciudad, región, país) si está autorizada."
    parameters_schema = {
        "type": "object",
        "properties": {
            "force_refresh": {"type": "boolean", "default": False}
        },
        "required": []
    }

    async def execute(self, force_refresh: bool = False, **kwargs) -> Dict[str, Any]:
        if not PermissionManager.is_granted(PermissionCategory.LOCATION):
            return {
                "success": False,
                "data": {},
                "error": "Permiso denegado: el acceso a la ubicación está desactivado (LOCATION)."
            }
        loc = LocationProvider.get_location(force_refresh=force_refresh)
        return {
            "success": loc.get("available", False),
            "data": loc,
            "error": loc.get("message") if not loc.get("available") else None
        }

class ParseTimeTool(BaseTool):
    name = "parse_relative_time"
    description = "Convierte expresiones relativas ('mañana a las 6', 'en 15 minutos', 'el próximo lunes') a una fecha/hora absoluta."
    parameters_schema = {
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "Expresión temporal a interpretar"}
        },
        "required": ["expression"]
    }

    async def execute(self, expression: str, **kwargs) -> Dict[str, Any]:
        parsed = TimeParser.parse(expression)
        return {
            "success": parsed.get("success", False),
            "data": parsed,
            "error": parsed.get("error")
        }

class PingTool(BaseTool):
    name = "ping"
    description = "Comprueba el estado operativo del sistema JARVIS."
    parameters_schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        return {
            "success": True,
            "data": {"status": "online", "message": "JARVIS operando normalmente."},
            "error": None
        }


class SetVolumeTool(BaseTool):
    name = "set_volume"
    description = (
        "Controla el volumen del sistema en Windows. "
        "Acepta un nivel del 0 al 100, o acción 'mute'/'unmute', o delta (+10/-10). "
        "Usa cuando el usuario pida subir, bajar, silenciar, reactivar o ajustar el volumen del equipo."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "level": {
                "type": "integer",
                "description": "Nivel de volumen absoluto del 0 al 100. Omitir si se usa action o delta.",
                "minimum": 0,
                "maximum": 100
            },
            "action": {
                "type": "string",
                "enum": ["mute", "unmute"],
                "description": "Acción especial: 'mute' para silenciar, 'unmute' para reactivar el audio."
            },
            "delta": {
                "type": "integer",
                "description": "Cambio relativo en puntos (+10 para subir, -10 para bajar). Se usa si no se especifica level."
            }
        },
        "required": []
    }

    async def execute(self, level: int = None, action: str = None, delta: int = None, **kwargs) -> Dict[str, Any]:
        if not PermissionManager.is_granted(PermissionCategory.AUTOMATION):
            return {
                "success": False,
                "data": {},
                "error": "Permiso denegado: la automatización del sistema está desactivada (AUTOMATION)."
            }
        res = await asyncio.to_thread(WindowsAutomationProvider.set_volume, level=level, action=action, delta=delta)
        return {
            "success": res.get("success", False),
            "data": res,
            "error": res.get("error") or res.get("message") if not res.get("success") else None
        }


