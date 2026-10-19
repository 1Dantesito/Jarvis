from typing import Dict, Any, Optional
from tools.router import BaseTool
from core.memory_manager import memory_manager

class CreateTaskTool(BaseTool):
    name = "create_task"
    description = "Crea una tarea o ítem en una lista personalizada o de pendientes del usuario."
    parameters_schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Título o contenido de la tarea o ítem"},
            "description": {"type": "string", "description": "Detalles o notas opcionales", "default": ""},
            "priority": {"type": "string", "enum": ["LOW", "NORMAL", "HIGH"], "default": "NORMAL"},
            "project": {"type": "string", "description": "Nombre de la lista personalizada o proyecto (ej. 'Compras', 'Trabajo', 'General')", "default": "General"}
        },
        "required": ["title"]
    }

    async def execute(self, title: str, description: str = "", priority: str = "NORMAL", project: str = "General", **kwargs) -> Dict[str, Any]:
        res = memory_manager.create_task(title=title, description=description, priority=priority, project=project)
        return res

class ListTasksTool(BaseTool):
    name = "list_tasks"
    description = "Obtiene las tareas o ítems de una lista personalizada o de pendientes del usuario."
    parameters_schema = {
        "type": "object",
        "properties": {
            "project": {"type": "string", "description": "Nombre opcional de la lista o proyecto para filtrar (ej. 'Compras', 'General')"}
        },
        "required": []
    }

    async def execute(self, project: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        tasks = memory_manager.list_tasks(include_completed=False, project=project)
        return {"success": True, "data": {"tasks": tasks, "project": project or "Todos"}, "error": None}

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
    description = "Elimina o vacía las tareas de una lista personalizada o todas las tareas acumuladas en el sistema."
    parameters_schema = {
        "type": "object",
        "properties": {
            "project": {"type": "string", "description": "Nombre opcional de la lista a vaciar (ej. 'Compras'). Si no se indica, vacía todas las tareas."}
        },
        "required": []
    }

    async def execute(self, project: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        res = memory_manager.clear_all_tasks(project=project)
        return res
