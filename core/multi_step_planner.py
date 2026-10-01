import uuid
import re
from typing import Dict, Any, List, Optional
from core.logger import logger
from core.security import SecurityPolicy, ActionRisk
from core.context_engine import ContextEngine
from core.memory_manager import memory_manager

class WorkflowStep:
    """
    Representa un paso atómico dentro de un plan multi-paso.
    """
    def __init__(
        self,
        step_id: int,
        tool_name: str,
        arguments: Dict[str, Any],
        description: str = "",
        requires_confirmation: bool = False
    ):
        self.step_id = step_id
        self.tool_name = tool_name
        self.arguments = arguments
        self.description = description or f"Ejecutar {tool_name}"
        self.requires_confirmation = requires_confirmation
        self.status = "pending"  # pending, waiting_confirmation, confirmed, running, completed, failed, cancelled
        self.result: Optional[Any] = None
        self.error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "description": self.description,
            "requires_confirmation": self.requires_confirmation,
            "status": self.status,
            "result": self.result,
            "error": self.error
        }

class WorkflowPlan:
    """
    Representa un flujo de trabajo compuesto de múltiples pasos encadenados.
    """
    def __init__(self, plan_id: str, title: str, steps: List[WorkflowStep]):
        self.plan_id = plan_id
        self.title = title
        self.steps = steps
        self.status = "created"  # created, waiting_confirmation, in_progress, completed, failed, cancelled
        self.current_step_index = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "title": self.title,
            "status": self.status,
            "current_step_index": self.current_step_index,
            "steps": [s.to_dict() for s in self.steps]
        }

class MultiStepPlanner:
    """
    Planificador y ejecutor de workflows complejos y tareas encadenadas (Roadmap Fase 18).
    Soporta descomposición de peticiones, validación de seguridad previa,
    modo interactivo con confirmación obligatoria para pasos de riesgo y reportes ejecutivos.
    """
    def __init__(self):
        self._active_plans: Dict[str, WorkflowPlan] = {}

    def get_plan(self, plan_id: str) -> Optional[WorkflowPlan]:
        return self._active_plans.get(plan_id)

    def create_plan(self, title: str, steps_data: List[Dict[str, Any]]) -> WorkflowPlan:
        plan_id = f"wf_{uuid.uuid4().hex[:8]}"
        steps = []
        for idx, s in enumerate(steps_data, start=1):
            tool_name = s.get("tool_name", "")
            args = s.get("arguments", {})
            desc = s.get("description", "")
            
            # Clasificación de riesgo con SecurityPolicy
            target = ""
            for k in ("target", "file_path", "filename", "app_name", "query", "url", "command", "location", "folder_path"):
                if k in args and isinstance(args[k], str):
                    target = args[k]
                    break
            if not target and args:
                target = " ".join(str(v) for v in args.values() if isinstance(v, (str, int, float)))

            risk = SecurityPolicy.classify_action(tool_name, target)
            requires_conf = (risk == ActionRisk.CONFIRMATION_REQUIRED) or s.get("requires_confirmation", False)

            step = WorkflowStep(
                step_id=idx,
                tool_name=tool_name,
                arguments=args,
                description=desc,
                requires_confirmation=requires_conf
            )
            if risk == ActionRisk.BLOCKED:
                step.status = "failed"
                step.error = f"Acción prohibida por política de seguridad: {tool_name}"
            steps.append(step)

        plan = WorkflowPlan(plan_id=plan_id, title=title, steps=steps)
        self._active_plans[plan_id] = plan
        logger.info(f"[MultiStepPlanner] Plan creado: {plan_id} ('{title}') con {len(steps)} pasos.")
        return plan

    def decompose_compound_request(self, prompt: str) -> Optional[WorkflowPlan]:
        """
        Detecta y descompone solicitudes compuestas en lenguaje natural en flujos multi-paso.
        """
        p = prompt.strip()
        low = p.lower()

        # Patrón 1: "pon música <X> y sube/ajusta el volumen (a <Y>)"
        m_music_vol = re.search(r'pon\s+(?:m[úu]sica\s+)?(.+?)\s+y\s+(?:sube|ajusta|pon)\s+el\s+volumen(?:\s+al?\s+(\d+))?', p, re.IGNORECASE)
        if m_music_vol:
            song = m_music_vol.group(1).strip()
            vol = int(m_music_vol.group(2)) if m_music_vol.group(2) else 80
            return self.create_plan(
                title=f"Reproducir {song} y ajustar volumen",
                steps_data=[
                    {"tool_name": "play_music", "arguments": {"query": song}, "description": f"Reproducir '{song}'"},
                    {"tool_name": "set_volume", "arguments": {"level": vol}, "description": f"Ajustar volumen a {vol}%"}
                ]
            )

        # Patrón 2: "crea una tarea <X> y un recordatorio <Y> para <Z>"
        m_task_rem = re.search(r'crea\s+(?:una\s+)?tarea\s+(.+?)\s+y\s+(?:crea\s+)?(?:un\s+)?recordatorio\s+(.+?)\s+para\s+(.+)', p, re.IGNORECASE)
        if m_task_rem:
            task_title = m_task_rem.group(1).strip()
            rem_title = m_task_rem.group(2).strip()
            rem_time = m_task_rem.group(3).strip()
            return self.create_plan(
                title="Crear tarea y recordatorio",
                steps_data=[
                    {"tool_name": "create_task", "arguments": {"title": task_title}, "description": f"Crear tarea '{task_title}'"},
                    {"tool_name": "create_reminder", "arguments": {"title": rem_title, "remind_at": rem_time}, "description": f"Crear recordatorio '{rem_title}' para {rem_time}"}
                ]
            )

        # Patrón 3: "busca <X> y recuérdame <Y> para <Z>"
        m_search_rem = re.search(r'busca\s+(.+?)\s+y\s+recu[eé]rdame\s+(.+?)\s+para\s+(.+)', p, re.IGNORECASE)
        if m_search_rem:
            query = m_search_rem.group(1).strip()
            rem_title = m_search_rem.group(2).strip()
            rem_time = m_search_rem.group(3).strip()
            return self.create_plan(
                title="Buscar y programar recordatorio",
                steps_data=[
                    {"tool_name": "web_search", "arguments": {"query": query}, "description": f"Buscar '{query}'"},
                    {"tool_name": "create_reminder", "arguments": {"title": rem_title, "remind_at": rem_time}, "description": f"Recordar '{rem_title}' para {rem_time}"}
                ]
            )

        return None

    async def execute_plan(
        self,
        plan_id: str,
        tool_router: Any,
        auto_confirm: bool = False
    ) -> Dict[str, Any]:
        plan = self.get_plan(plan_id)
        if not plan:
            return {"success": False, "status": "not_found", "error": f"Plan no encontrado: {plan_id}"}

        plan.status = "in_progress"
        last_result = None

        while plan.current_step_index < len(plan.steps):
            step = plan.steps[plan.current_step_index]

            # Si el paso ya falló en validación previa (ej. acción bloqueada)
            if step.status == "failed":
                plan.status = "failed"
                return {
                    "success": False,
                    "status": "failed",
                    "plan_id": plan_id,
                    "failed_step": step.to_dict(),
                    "error": step.error
                }

            # Si el paso requiere confirmación y aún no fue confirmado
            if step.requires_confirmation and step.status != "confirmed" and not auto_confirm:
                step.status = "waiting_confirmation"
                plan.status = "waiting_confirmation"
                logger.info(f"[MultiStepPlanner] Plan {plan_id} en espera de confirmación para paso #{step.step_id} ('{step.description}')")
                return {
                    "success": False,
                    "status": "waiting_confirmation",
                    "plan_id": plan_id,
                    "step_id": step.step_id,
                    "tool_name": step.tool_name,
                    "description": step.description,
                    "arguments": step.arguments,
                    "message": f"El paso '{step.description}' requiere confirmación explícita antes de continuar."
                }

            step.status = "running"
            try:
                # Interpolación de resultados previos en argumentos
                resolved_args = {}
                for k, v in step.arguments.items():
                    if isinstance(v, str) and "{{previous_result}}" in v and last_result is not None:
                        resolved_args[k] = v.replace("{{previous_result}}", str(last_result))
                    else:
                        resolved_args[k] = v

                exec_res = await tool_router.execute_tool(step.tool_name, resolved_args)
                if not exec_res.get("success", False):
                    step.status = "failed"
                    step.error = exec_res.get("error", "Error en ejecución de herramienta.")
                    plan.status = "failed"
                    logger.warning(f"[MultiStepPlanner] Falló paso #{step.step_id} en plan {plan_id}: {step.error}")
                    return {
                        "success": False,
                        "status": "failed",
                        "plan_id": plan_id,
                        "failed_step": step.to_dict(),
                        "error": step.error
                    }

                step.status = "completed"
                step.result = exec_res.get("data")
                last_result = step.result
                plan.current_step_index += 1

            except Exception as e:
                step.status = "failed"
                step.error = str(e)
                plan.status = "failed"
                logger.error(f"[MultiStepPlanner] Excepción en paso #{step.step_id} del plan {plan_id}: {e}")
                return {
                    "success": False,
                    "status": "failed",
                    "plan_id": plan_id,
                    "failed_step": step.to_dict(),
                    "error": str(e)
                }

        plan.status = "completed"
        logger.info(f"[MultiStepPlanner] Plan {plan_id} completado con éxito ({len(plan.steps)} pasos ejecutados).")
        return {
            "success": True,
            "status": "completed",
            "plan_id": plan_id,
            "steps_executed": len(plan.steps),
            "results": [s.to_dict() for s in plan.steps]
        }

    async def confirm_step(
        self,
        plan_id: str,
        step_id: int,
        confirmed: bool,
        tool_router: Any
    ) -> Dict[str, Any]:
        plan = self.get_plan(plan_id)
        if not plan:
            return {"success": False, "status": "not_found", "error": f"Plan no encontrado: {plan_id}"}

        target_step = None
        for s in plan.steps:
            if s.step_id == step_id:
                target_step = s
                break

        if not target_step:
            return {"success": False, "status": "step_not_found", "error": f"Paso #{step_id} no encontrado en plan {plan_id}."}

        if not confirmed:
            target_step.status = "cancelled"
            plan.status = "cancelled"
            logger.info(f"[MultiStepPlanner] Paso #{step_id} rechazado por el usuario. Plan {plan_id} cancelado.")
            return {"success": True, "status": "cancelled", "plan_id": plan_id, "message": "Paso cancelado por el usuario."}

        target_step.status = "confirmed"
        return await self.execute_plan(plan_id, tool_router=tool_router)

    def generate_daily_briefing(self, period: str = "auto") -> Dict[str, Any]:
        """
        Genera reporte ejecutivo matutino o vespertino consolidando tareas, recordatorios y contexto.
        """
        dt_info = ContextEngine.get_current_datetime_dict()
        now_hour = dt_info.get("hour")
        if now_hour is None:
            from datetime import datetime
            now_hour = datetime.now().hour

        resolved_period = (period or "auto").lower()
        if resolved_period == "auto":
            resolved_period = "morning" if now_hour < 14 else "evening"

        tasks = memory_manager.list_tasks(include_completed=False)
        reminders = memory_manager.list_reminders(include_completed=False)

        high_tasks = [t for t in tasks if (t.get("priority") or "").upper() in ["HIGH", "URGENT"]]
        total_tasks = len(tasks)
        total_rems = len(reminders)

        date_str = dt_info.get("date", "hoy")
        time_str = dt_info.get("time_12h", "")

        if resolved_period == "morning":
            greeting = f"Buenos días. Hoy es {date_str}."
            if total_tasks == 0 and total_rems == 0:
                summary_text = f"{greeting} No tienes tareas ni recordatorios pendientes para hoy. Todo despejado."
            else:
                summary_text = (
                    f"{greeting} Tienes {total_tasks} {'tarea pendiente' if total_tasks == 1 else 'tareas pendientes'}"
                    + (f" ({len(high_tasks)} de alta prioridad)" if high_tasks else "")
                    + f" y {total_rems} {'recordatorio programado' if total_rems == 1 else 'recordatorios programados'}."
                )
        else:
            greeting = f"Buenas noches. Resumen al cierre de hoy, {date_str}."
            if total_tasks == 0:
                summary_text = f"{greeting} Completaste todas tus tareas del día. No tienes pendientes para mañana."
            else:
                summary_text = (
                    f"{greeting} Tienes {total_tasks} {'tarea pendiente' if total_tasks == 1 else 'tareas pendientes'} para mañana"
                    + (f" ({len(high_tasks)} prioritarias)" if high_tasks else "")
                    + f" y {total_rems} recordatorios en agenda."
                )

        return {
            "success": True,
            "data": {
                "period": resolved_period,
                "date": date_str,
                "time": time_str,
                "total_tasks": total_tasks,
                "high_priority_tasks": len(high_tasks),
                "tasks": tasks[:10],
                "total_reminders": total_rems,
                "reminders": reminders[:10],
                "briefing_text": summary_text
            },
            "error": None
        }

multi_step_planner = MultiStepPlanner()
