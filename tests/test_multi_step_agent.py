import pytest
from core.multi_step_planner import MultiStepPlanner, WorkflowStep, WorkflowPlan
from core.memory_manager import memory_manager
from tools.router import ToolRouter, ToolType, TOOL_REGISTRY
from tools.implementations.automation_tools import ExecuteWorkflowTool, DailyBriefingTool
from tools.implementations.task_tools import CreateTaskTool, ListTasksTool
from tools.implementations.system_tools import PingTool
from core.orchestrator import JarvisOrchestrator

@pytest.mark.asyncio
async def test_multi_step_planner_create_and_validate_plan():
    planner = MultiStepPlanner()
    plan = planner.create_plan(
        title="Test Safe Workflow",
        steps_data=[
            {"tool_name": "ping", "arguments": {}, "description": "Hacer ping"},
            {"tool_name": "create_task", "arguments": {"title": "Tarea multi-paso 1"}, "description": "Crear tarea"}
        ]
    )
    assert plan.title == "Test Safe Workflow"
    assert len(plan.steps) == 2
    assert plan.steps[0].requires_confirmation is False
    assert plan.steps[1].requires_confirmation is False

@pytest.mark.asyncio
async def test_multi_step_planner_flags_confirmation_required():
    planner = MultiStepPlanner()
    # clear_all_tasks está en CONFIRMATION_ACTIONS
    plan = planner.create_plan(
        title="Workflow con confirmación",
        steps_data=[
            {"tool_name": "ping", "arguments": {}},
            {"tool_name": "clear_all_tasks", "arguments": {}}
        ]
    )
    assert len(plan.steps) == 2
    assert plan.steps[0].requires_confirmation is False
    assert plan.steps[1].requires_confirmation is True

@pytest.mark.asyncio
async def test_multi_step_planner_blocks_forbidden_action():
    planner = MultiStepPlanner()
    # delete_file es una acción permanentemente bloqueada por SecurityPolicy
    plan = planner.create_plan(
        title="Workflow con acción prohibida",
        steps_data=[
            {"tool_name": "delete_file", "arguments": {"file_path": "test.txt"}}
        ]
    )
    assert plan.steps[0].status == "failed"
    assert "prohibida por política de seguridad" in plan.steps[0].error

@pytest.mark.asyncio
async def test_multi_step_planner_execution_lifecycle():
    router = ToolRouter()
    router.register_tool(PingTool())
    router.register_tool(CreateTaskTool())
    router.register_tool(ListTasksTool())

    planner = MultiStepPlanner()
    plan = planner.create_plan(
        title="Flujo ejecutable",
        steps_data=[
            {"tool_name": "ping", "arguments": {}, "description": "Paso 1: Ping"},
            {"tool_name": "create_task", "arguments": {"title": "MultiStep Task Alpha"}, "description": "Paso 2: Crear Tarea"}
        ]
    )

    res = await planner.execute_plan(plan.plan_id, tool_router=router)
    assert res["success"] is True
    assert res["status"] == "completed"
    assert res["steps_executed"] == 2
    assert plan.status == "completed"

@pytest.mark.asyncio
async def test_multi_step_planner_interactive_confirmation_flow():
    router = ToolRouter()
    router.register_tool(PingTool())

    planner = MultiStepPlanner()
    # Creamos un plan con un paso que explícitamente requiere confirmación
    plan = planner.create_plan(
        title="Flujo interactivo",
        steps_data=[
            {"tool_name": "ping", "arguments": {}, "description": "Paso 1 seguro"},
            {"tool_name": "ping", "arguments": {}, "description": "Paso 2 delicado", "requires_confirmation": True}
        ]
    )

    # 1. Primera ejecución: debe detenerse en el paso 2
    res_pause = await planner.execute_plan(plan.plan_id, tool_router=router)
    assert res_pause["success"] is False
    assert res_pause["status"] == "waiting_confirmation"
    assert res_pause["step_id"] == 2

    # 2. Rechazo de confirmación
    res_cancel = await planner.confirm_step(plan.plan_id, step_id=2, confirmed=False, tool_router=router)
    assert res_cancel["success"] is True
    assert res_cancel["status"] == "cancelled"
    assert plan.status == "cancelled"

    # 3. Flujo con aprobación
    plan2 = planner.create_plan(
        title="Flujo aprobado",
        steps_data=[
            {"tool_name": "ping", "arguments": {}, "description": "Paso 1"},
            {"tool_name": "ping", "arguments": {}, "description": "Paso 2", "requires_confirmation": True}
        ]
    )
    res_pause2 = await planner.execute_plan(plan2.plan_id, tool_router=router)
    assert res_pause2["status"] == "waiting_confirmation"

    res_approve = await planner.confirm_step(plan2.plan_id, step_id=2, confirmed=True, tool_router=router)
    assert res_approve["success"] is True
    assert res_approve["status"] == "completed"
    assert plan2.status == "completed"

@pytest.mark.asyncio
async def test_decompose_compound_request():
    planner = MultiStepPlanner()
    
    # Caso 1: Tarea y recordatorio
    plan1 = planner.decompose_compound_request("crea una tarea Comprar café y un recordatorio Llamar al médico para mañana a las 10 am")
    assert plan1 is not None
    assert len(plan1.steps) == 2
    assert plan1.steps[0].tool_name == "create_task"
    assert "Comprar café" in plan1.steps[0].arguments["title"]
    assert plan1.steps[1].tool_name == "create_reminder"

    # Caso 2: Música y volumen
    plan2 = planner.decompose_compound_request("pon música Bohemian Rhapsody y sube el volumen al 75")
    assert plan2 is not None
    assert len(plan2.steps) == 2
    assert plan2.steps[0].tool_name == "play_music"
    assert plan2.steps[1].tool_name == "set_volume"
    assert plan2.steps[1].arguments["level"] == 75

@pytest.mark.asyncio
async def test_daily_briefing_generation():
    planner = MultiStepPlanner()
    # Matutino
    morning = planner.generate_daily_briefing(period="morning")
    assert morning["success"] is True
    assert "Buenos días" in morning["data"]["briefing_text"]
    assert "total_tasks" in morning["data"]
    assert "total_reminders" in morning["data"]

    # Vespertino
    evening = planner.generate_daily_briefing(period="evening")
    assert evening["success"] is True
    assert "Buenas noches" in evening["data"]["briefing_text"]

@pytest.mark.asyncio
async def test_automation_tools_in_router_and_orchestrator():
    from providers.mock_provider import MockAIProvider
    orch = JarvisOrchestrator(primary_provider=MockAIProvider())
    assert "execute_workflow" in orch.tool_router._tools
    assert "get_daily_briefing" in orch.tool_router._tools
    assert TOOL_REGISTRY["execute_workflow"] == ToolType.ACTION
    assert TOOL_REGISTRY["get_daily_briefing"] == ToolType.QUERY

    # Probar DailyBriefingTool vía router
    res = await orch.tool_router.execute_tool("get_daily_briefing", {"period": "morning"})
    assert res["success"] is True
    assert "briefing_text" in res["data"]
