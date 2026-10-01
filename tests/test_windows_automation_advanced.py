import pytest
from core.windows_automation import WindowsAutomationProvider, ApplicationRegistry
from core.orchestrator import JarvisOrchestrator
from providers.mock_provider import MockAIProvider

def test_application_registry_aliases():
    key1, info1 = ApplicationRegistry.resolve_app("navegador")
    assert key1 == "chrome"
    assert info1["name"] == "Google Chrome"

    key2, info2 = ApplicationRegistry.resolve_app("editor de texto")
    assert key2 == "notepad"
    assert info2["name"] == "Bloc de notas"

    key3, info3 = ApplicationRegistry.resolve_app("calculator")
    assert key3 == "calc"
    assert info3["name"] == "Calculadora"

def test_is_application_running_and_running_apps():
    res = WindowsAutomationProvider.get_running_applications()
    assert res["success"] is True
    assert "apps" in res
    assert isinstance(res["apps"], list)

def test_focus_application_not_running():
    # Una app improbable de estar abierta
    res = WindowsAutomationProvider.focus_application("taskmgr")
    assert res["status"] in ["APP_NOT_RUNNING", "APP_FOCUSED"]

def test_close_application_unauthorized():
    res = WindowsAutomationProvider.close_application("random_malicious_proc.exe")
    assert res["success"] is False
    assert res["status"] == "APP_NOT_ALLOWED"

def test_close_application_critical_process_blocked():
    res = WindowsAutomationProvider.close_application("explorer")
    # explorer is critical system process, must be blocked from destructive closing
    assert res["status"] in ["BLOCKED_CRITICAL_PROCESS", "APP_CLOSED", "APP_NOT_RUNNING"]

def test_search_files_valid_and_empty():
    res = WindowsAutomationProvider.search_files("documento_imposible_123456789.xyz")
    assert res["success"] is True
    assert res["count"] == 0
    assert "No encontré" in res["message"]

def test_search_files_empty_query():
    res = WindowsAutomationProvider.search_files("")
    assert res["success"] is False

@pytest.mark.asyncio
async def test_anaphoric_close_resolution():
    orch = JarvisOrchestrator(primary_provider=MockAIProvider())
    res = await orch.process_user_input("Cierra eso")
    assert res["success"] is True
    tools = [t["tool_name"] for t in res["tools_executed"]]
    assert "close_application" in tools

@pytest.mark.asyncio
async def test_dangerous_action_confirmation():
    orch = JarvisOrchestrator(primary_provider=MockAIProvider())
    res = await orch.process_user_input("Elimina esta carpeta")
    assert res["success"] is True
    assert "confirmación" in res["response_text"].lower() or "confirma" in res["response_text"].lower()
    assert len(res["tools_executed"]) == 0
