import pytest
from unittest.mock import patch, MagicMock
from tools.implementations.desktop_tools import AnalyzeScreenTool
from tools.router import ToolRouter, ToolType

def test_analyze_screen_metadata():
    tool = AnalyzeScreenTool()
    assert tool.name == "analyze_screen"
    router = ToolRouter()
    assert router.get_tool_type("analyze_screen") == ToolType.QUERY

@pytest.mark.asyncio
async def test_analyze_screen_privacy_filter():
    tool = AnalyzeScreenTool()

    # 1. Ventana sensible (gestor de contraseñas)
    mock_app_sensitive = {
        "available": True,
        "title": "Bitwarden - Mis Contraseñas",
        "app_name": "Bitwarden",
        "process": "bitwarden.exe"
    }

    with patch("core.windows_automation.WindowsAutomationProvider.get_active_application", return_value=mock_app_sensitive):
        res = await tool.execute(prompt="¿Qué dice la pantalla?")
        assert res["success"] is False
        assert res["data"]["privacy_blocked"] is True
        assert "privacidad" in res["error"].lower()

@pytest.mark.asyncio
async def test_analyze_screen_safe_capture():
    tool = AnalyzeScreenTool()

    mock_app_safe = {
        "available": True,
        "title": "Documento Técnico - Visual Studio Code",
        "app_name": "Code",
        "process": "code.exe"
    }

    # Mock ImageGrab de PIL
    from PIL import Image
    fake_img = Image.new("RGB", (800, 600), color="blue")

    with patch("core.windows_automation.WindowsAutomationProvider.get_active_application", return_value=mock_app_safe):
        with patch("PIL.ImageGrab.grab", return_value=fake_img):
            res = await tool.execute(prompt="¿Qué código se observa?")
            assert res["success"] is True
            assert "data_url" in res["data"]
            assert res["data"]["data_url"].startswith("data:image/jpeg;base64,")
            assert res["data"]["width"] == 800
            assert res["data"]["height"] == 600

@pytest.mark.asyncio
async def test_analyze_screen_platform_restricted():
    from core.config import settings
    tool = AnalyzeScreenTool()
    orig_env = settings.ENV
    try:
        settings.ENV = "mobile-dev"
        res = await tool.execute(prompt="analiza pantalla")
        assert res["success"] is False
        assert res["data"]["platform_restricted"] is True
    finally:
        settings.ENV = orig_env
