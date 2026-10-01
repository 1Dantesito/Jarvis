from typing import Dict, Any
from tools.router import BaseTool
from core.memory_manager import memory_manager

class CreateTaskTool(BaseTool):
    name = "create_task"
    description = "Crea una tarea en la lista de pendientes del usuario."
    parameters_schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Título de la tarea"},
            "description": {"type": "string", "description": "Detalles opcionales", "default": ""},
            "priority": {"type": "string", "enum": ["LOW", "NORMAL", "HIGH"], "default": "NORMAL"}
        },
        "required": ["title"]
    }

    async def execute(self, title: str, description: str = "", priority: str = "NORMAL", **kwargs) -> Dict[str, Any]:
        res = memory_manager.create_task(title=title, description=description, priority=priority)
        return res

class ListTasksTool(BaseTool):
    name = "list_tasks"
    description = "Obtiene las tareas pendientes del usuario."
    parameters_schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        tasks = memory_manager.list_tasks(include_completed=False)
        return {"success": True, "data": {"tasks": tasks}, "error": None}

class CompleteTaskTool(BaseTool):
    name = "complete_task"
    description = "Marca una tarea como completada o realizada."
    parameters_schema = {
        "type": "object",
        "properties": {
            "task_id": {"type": "integer", "description": "ID numérico de la tarea"}
        },
        "required": ["task_id"]
    }

    async def execute(self, task_id: int, **kwargs) -> Dict[str, Any]:
        ok = memory_manager.complete_task(task_id=task_id)
        if ok:
            return {"success": True, "data": {"task_id": task_id, "message": f"Tarea #{task_id} completada."}, "error": None}
        return {"success": False, "data": {}, "error": f"No se encontró la tarea #{task_id}."}

class DeleteTaskTool(BaseTool):
    name = "delete_task"
    description = "Elimina o borra una tarea específica por ID o título."
    parameters_schema = {
        "type": "object",
        "properties": {
            "task_id_or_title": {"type": "string", "description": "ID numérico o título de la tarea a borrar"}
        },
        "required": ["task_id_or_title"]
    }

    async def execute(self, task_id_or_title: str, **kwargs) -> Dict[str, Any]:
        res = memory_manager.delete_task(task_id_or_title)
        return res

class ClearTasksTool(BaseTool):
    name = "clear_all_tasks"
    description = "Elimina o vacía todas las tareas acumuladas en el sistema."
    parameters_schema = {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs) -> Dict[str, Any]:
        res = memory_manager.clear_all_tasks()
        return res
