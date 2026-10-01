import pytest
from core.system_capabilities import SystemCapabilities
from core.permissions import PermissionManager, PermissionCategory, PermissionState

def test_connectivity_check():
    is_online = SystemCapabilities.check_internet_connectivity()
    assert isinstance(is_online, bool)

def test_microphone_status():
    mic = SystemCapabilities.get_microphone_status()
    assert "available" in mic
    assert "devices_count" in mic
    assert isinstance(mic["devices_count"], int)

def test_environmental_status():
    env = SystemCapabilities.get_full_environmental_status()
    assert "connectivity" in env
    assert "microphone" in env
    assert "os" in env
    assert "active_app" in env

def test_effective_permission_matrix():
    matrix = PermissionManager.get_effective_matrix()
    assert "microphone" in matrix
    assert "location" in matrix
    assert "notifications" in matrix
    assert "user_permission" in matrix["microphone"]
    assert "system_capability" in matrix["microphone"]
    assert "is_operational" in matrix["microphone"]

@pytest.mark.asyncio
async def test_platform_capabilities_layer():
    from core.platform_capabilities import PlatformCapabilities, PlatformType
    from tools.implementations.desktop_tools import OpenUrlTool, FocusAppTool, OpenFileTool
    from tools.router import ToolRouter

    # 1. Desktop tools permitidas en desktop
    is_sup, err = PlatformCapabilities.is_tool_supported("open_url", target_platform=PlatformType.DESKTOP.value)
    assert is_sup is True
    assert err is None

    # 2. Desktop tools bloqueadas en móvil
    is_sup_mob, err_mob = PlatformCapabilities.is_tool_supported("open_url", target_platform=PlatformType.MOBILE.value)
    assert is_sup_mob is False
    assert "solo está disponible en la versión de escritorio" in err_mob

    # 3. Verificación de ejecución directa en la herramienta con target_platform móvil
    # Simulando entorno móvil
    from core.config import settings
    orig_env = settings.ENV
    try:
        settings.ENV = "mobile-dev"
        url_res = await OpenUrlTool().execute(url="https://google.com")
        assert url_res["success"] is False
        assert url_res["data"]["platform_restricted"] is True

        focus_res = await FocusAppTool().execute(app_name="calc")
        assert focus_res["success"] is False
        assert focus_res["data"]["platform_restricted"] is True

        router = ToolRouter()
        router.register_tool(OpenUrlTool())
        exec_res = await router.execute_tool("open_url", {"url": "https://google.com"})
        assert exec_res["success"] is False
        assert exec_res["data"]["platform_restricted"] is True
    finally:
        settings.ENV = orig_env

