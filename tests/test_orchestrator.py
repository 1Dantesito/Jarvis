import pytest
from core.orchestrator import JarvisOrchestrator
from providers.mock_provider import MockAIProvider

@pytest.mark.asyncio
async def test_orchestrator_flow():
    orch = JarvisOrchestrator(primary_provider=MockAIProvider())

    res_time = await orch.process_user_input("¿Qué hora es?")
    assert res_time["success"] is True
    assert "Son las" in res_time["response_text"] or ":" in res_time["response_text"]
    assert any(t["tool_name"] == "get_current_datetime" for t in res_time["tools_executed"])

    res_app = await orch.process_user_input("Abre la calculadora")
    assert res_app["success"] is True
    assert "calculadora" in res_app["response_text"].lower() or "abriendo" in res_app["response_text"].lower()
    assert any(t["tool_name"] == "open_application" for t in res_app["tools_executed"])

    res_task = await orch.process_user_input("Crear tarea revisar código")
    assert res_task["success"] is True
    assert any(t["tool_name"] == "create_task" for t in res_task["tools_executed"])

def test_orchestrator_registers_universal_and_desktop_tools():
    orch = JarvisOrchestrator(primary_provider=MockAIProvider())
    tools = orch.tool_router._tools
    # Universales (Punto 5)
    assert "parse_relative_time" in tools
    assert "list_reminders" in tools
    assert "snooze_reminder" in tools
    assert "complete_reminder" in tools
    assert "export_memory" in tools
    # Desktop (Punto 4)
    assert "focus_application" in tools
    assert "get_running_applications" in tools
    assert "open_url" in tools
    assert "open_file" in tools
    assert "open_folder" in tools
    assert "get_active_application" in tools
    assert "analyze_screen" in tools
    # Web y Workflows (Punto 6 y Fase 18)
    assert "read_webpage" in tools
    assert "execute_workflow" in tools
    assert "get_daily_briefing" in tools


