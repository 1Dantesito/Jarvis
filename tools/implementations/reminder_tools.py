from typing import Dict, Any, Optional
from tools.router import BaseTool
from core.memory_manager import memory_manager
from core.permissions import PermissionManager, PermissionCategory

class CreateReminderTool(BaseTool):
    name = "create_reminder"
    description = "Crea un recordatorio autónomo proactivo con fecha/hora relativa o absoluta y prioridad."
    parameters_schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Descripción del recordatorio"},
            "remind_at": {"type": "string", "description": "Hora o fecha objetivo (ej. '18:00', 'mañana a las 6 pm', 'en 15 minutos')"},
            "priority": {"type": "string", "enum": ["LOW", "NORMAL", "HIGH", "URGENT"], "default": "NORMAL"},
            "description": {"type": "string", "description": "Detalles adicionales opcionales", "default": ""}
        },
        "required": ["title", "remind_at"]
    }

    async def execute(
        self,
        title: Optional[str] = None,
        remind_at: Optional[str] = None,
        priority: str = "NORMAL",
        description: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        if not PermissionManager.is_granted(PermissionCategory.NOTIFICATIONS):
            return {
                "success": False,
                "data": {},
                "error": "Permiso denegado: las notificaciones están desactivadas (NOTIFICATIONS)."
            }

        clean_title = (
            title or
            kwargs.get("text") or
            kwargs.get("content") or
            kwargs.get("task") or
            kwargs.get("reminder") or
            kwargs.get("name") or
            kwargs.get("message") or
            "Recordatorio"
        ).strip()

        clean_remind_at = (
            remind_at or
            kwargs.get("time") or
            kwargs.get("date") or
            kwargs.get("datetime") or
            kwargs.get("when") or
            kwargs.get("target_time") or
            kwargs.get("remind_time") or
            kwargs.get("expression") or
            kwargs.get("remind_at_expression") or
            kwargs.get("at") or
            description or
            "en 1 hora"
        ).strip()

        clean_prio = (priority or kwargs.get("priority") or "NORMAL").upper()

        res = memory_manager.create_reminder(
            title=clean_title,
            remind_at_expression=clean_remind_at,
            priority=clean_prio,
            description=description
        )
        return res

class ListRemindersTool(BaseTool):
    name = "list_reminders"
    description = "Consulta la lista de recordatorios activos o pendientes."
    parameters_schema = {
        "type": "object",
        "properties": {
            "include_completed": {"type": "boolean", "default": False}
        },
        "required": []
    }

    async def execute(self, include_completed: bool = False, **kwargs) -> Dict[str, Any]:
        rems = memory_manager.list_reminders(include_completed=include_completed)
        return {"success": True, "data": {"reminders": rems, "count": len(rems)}, "error": None}

class SnoozeReminderTool(BaseTool):
    name = "snooze_reminder"
    description = "Pospone un recordatorio existente por una cantidad de minutos (por defecto 10 minutos)."
    parameters_schema = {
        "type": "object",
        "properties": {
            "reminder_id": {"type": "integer", "description": "ID del recordatorio a posponer"},
            "minutes": {"type": "integer", "default": 10, "description": "Minutos adicionales"}
        },
        "required": ["reminder_id"]
    }

    async def execute(self, reminder_id: int, minutes: int = 10, **kwargs) -> Dict[str, Any]:
        res = memory_manager.snooze_reminder(reminder_id=reminder_id, minutes=minutes)
        return res

class CompleteReminderTool(BaseTool):
    name = "complete_reminder"
    description = "Marca un recordatorio como completado o realizado."
    parameters_schema = {
        "type": "object",
        "properties": {
            "reminder_id": {"type": "integer", "description": "ID del recordatorio"}
        },
        "required": ["reminder_id"]
    }

    async def execute(self, reminder_id: int, **kwargs) -> Dict[str, Any]:
        ok = memory_manager.complete_reminder(reminder_id=reminder_id)
        if ok:
            return {"success": True, "data": {"reminder_id": reminder_id, "message": f"Recordatorio #{reminder_id} completado."}, "error": None}
        return {"success": False, "data": {}, "error": f"No se encontró el recordatorio #{reminder_id}."}

class DeleteReminderTool(BaseTool):
    name = "delete_reminder"
    description = "Elimina o borra un recordatorio específico por ID o por título."
    parameters_schema = {
        "type": "object",
        "properties": {
            "reminder_id_or_title": {"type": "string", "description": "ID numérico o título del recordatorio a borrar"}
        },
        "required": ["reminder_id_or_title"]
    }

    async def execute(self, reminder_id_or_title: str, **kwargs) -> Dict[str, Any]:
        res = memory_manager.delete_reminder(reminder_id_or_title)
        return res

class ClearRemindersTool(BaseTool):
    name = "clear_all_reminders"
    description = "Elimina o vacía todos los recordatorios acumulados en el sistema."
    parameters_schema = {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs) -> Dict[str, Any]:
        res = memory_manager.clear_all_reminders()
        return res

class ClearAllPendingTool(BaseTool):
    name = "clear_all_pending"
    description = "Elimina y vacía simultáneamente todos los recordatorios y tareas acumuladas ('borra eso', 'borra todos mis pendientes', 'borra las tareas y recordatorios')."
    parameters_schema = {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs) -> Dict[str, Any]:
        res = memory_manager.clear_all_pending()
        return res

class PendingSummaryTool(BaseTool):
    name = "get_pending_summary"
    description = "Obtiene un resumen consolidado de todas las tareas y recordatorios pendientes del usuario."
    parameters_schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        data = memory_manager.get_pending_summary()
        return {"success": True, "data": data, "error": None}
