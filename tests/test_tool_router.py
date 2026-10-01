import pytest
from tools.router import ToolRouter
from tools.implementations.system_tools import CurrentDatetimeTool, PingTool

@pytest.mark.asyncio
async def test_tool_registration_and_execution():
    router = ToolRouter()
    router.register_tool(CurrentDatetimeTool())
    router.register_tool(PingTool())

    schemas = router.get_tools_schema_anthropic()
    assert len(schemas) == 2
    tool_names = [s["name"] for s in schemas]
    assert "get_current_datetime" in tool_names
    assert "ping" in tool_names

    res_ping = await router.execute_tool("ping", {})
    assert res_ping["success"] is True
    assert res_ping["data"]["status"] == "online"

    res_time = await router.execute_tool("get_current_datetime", {})
    assert res_time["success"] is True
    assert "time_12h" in res_time["data"]

    res_invalid = await router.execute_tool("non_existing_tool", {})
    assert res_invalid["success"] is False

@pytest.mark.asyncio
async def test_schemas_anthropic_gemini_openai():
    from tools.implementations.system_tools import SetVolumeTool
    from tools.implementations.desktop_tools import SearchFilesTool

    router = ToolRouter()
    router.register_tool(SetVolumeTool())
    router.register_tool(SearchFilesTool())

    # Anthropic
    anthropic_schemas = router.get_tools_schema_anthropic()
    assert len(anthropic_schemas) == 2
    assert "input_schema" in anthropic_schemas[0]

    # Gemini
    gemini_schemas = router.get_tools_schema_gemini()
    assert len(gemini_schemas) == 2
    assert "parameters" in gemini_schemas[0]

    # OpenAI / OpenRouter
    openai_schemas = router.get_tools_schema_openai()
    assert len(openai_schemas) == 2
    for s in openai_schemas:
        assert s["type"] == "function"
        assert "name" in s["function"]
        assert "description" in s["function"]
        assert "parameters" in s["function"]

@pytest.mark.asyncio
async def test_tool_router_security_interception():
    from tools.implementations.desktop_tools import OpenAppTool, SearchFilesTool
    router = ToolRouter()
    router.register_tool(OpenAppTool())
    router.register_tool(SearchFilesTool())

    # 1. Bloqueo explícito de acciones de eliminación
    res_delete = await router.execute_tool("delete_file", {"target": "reporte.docx"})
    assert res_delete["success"] is False
    assert "ALLOWLIST" in res_delete["error"]

    # 2. Bloqueo por inyección de comandos en argumentos
    res_inject = await router.execute_tool("open_application", {"app_name": "calc.exe; shutdown -s"})
    assert res_inject["success"] is False
    assert "ALLOWLIST" in res_inject["error"]

    res_pipe = await router.execute_tool("search_files", {"query": "archivo | del /f"})
    assert res_pipe["success"] is False
    assert "ALLOWLIST" in res_pipe["error"]

    # 3. Acción no permitida por Fail-Closed
    res_unknown = await router.execute_tool("arbitrary_execution", {"cmd": "dir"})
    assert res_unknown["success"] is False
    assert "ALLOWLIST" in res_unknown["error"]

@pytest.mark.asyncio
async def test_tool_router_set_volume_execution():
    from tools.implementations.system_tools import SetVolumeTool
    router = ToolRouter()
    router.register_tool(SetVolumeTool())

    res_vol = await router.execute_tool("set_volume", {"level": 25})
    assert res_vol["success"] is True
    assert res_vol["data"]["level"] == 25

    res_mute = await router.execute_tool("set_volume", {"action": "mute"})
    assert res_mute["success"] is True
    assert res_mute["data"]["status"] == "MUTED"

