from typing import Dict, Any, List, Optional
from tools.router import BaseTool, ToolType
from core.multi_step_planner import multi_step_planner

class ExecuteWorkflowTool(BaseTool):
    name = "execute_workflow"
    description = "Ejecuta una secuencia multi-paso encadenada de herramientas con control de flujo, seguridad previa y confirmación interactiva."
    tool_type = ToolType.ACTION
    parameters_schema = {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Título o descripción general del flujo de trabajo",
                "default": "Flujo automatizado"
            },
            "steps": {
                "type": "array",
                "description": "Lista ordenada de pasos a ejecutar secuencialmente",
                "items": {
                    "type": "object",
                    "properties": {
                        "tool_name": {"type": "string", "description": "Nombre de la herramienta"},
                        "arguments": {"type": "object", "description": "Diccionario de argumentos para la herramienta"},
                        "description": {"type": "string", "description": "Descripción humana del paso"},
                        "requires_confirmation": {"type": "boolean", "description": "Si este paso requiere confirmación explícita previa", "default": False}
                    },
                    "required": ["tool_name"]
                }
            },
            "auto_confirm": {
                "type": "boolean",
                "description": "Si es True, omite pausas de confirmación interactiva",
                "default": False
            }
        },
        "required": ["steps"]
    }

    def __init__(self, router=None):
        self._router = router

    def set_router(self, router):
        self._router = router

    async def execute(self, steps: List[Dict[str, Any]], title: str = "Flujo automatizado", auto_confirm: bool = False, **kwargs) -> Dict[str, Any]:
        router = self._router
        if not router:
            from tools.router import ToolRouter
            router = ToolRouter()

        plan = multi_step_planner.create_plan(title=title, steps_data=steps)
        res = await multi_step_planner.execute_plan(plan.plan_id, tool_router=router, auto_confirm=auto_confirm)
        return {
            "success": res.get("success", False),
            "data": res,
            "error": res.get("error")
        }

class DailyBriefingTool(BaseTool):
    name = "get_daily_briefing"
    description = "Genera un reporte ejecutivo diario matutino o vespertino con resumen de tareas pendientes, recordatorios y estado general."
    tool_type = ToolType.QUERY
    parameters_schema = {
        "type": "object",
        "properties": {
            "period": {
                "type": "string",
                "enum": ["morning", "evening", "auto"],
                "default": "auto",
                "description": "Período del día para el reporte (matutino, vespertino o detección automática según la hora)"
            }
        },
        "required": []
    }

    async def execute(self, period: str = "auto", **kwargs) -> Dict[str, Any]:
        res = multi_step_planner.generate_daily_briefing(period=period)
        return res
