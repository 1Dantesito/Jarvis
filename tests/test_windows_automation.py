import pytest
from core.windows_automation import ApplicationRegistry, WindowsAutomationProvider
from core.security import SecurityPolicy, ActionRisk

def test_application_registry_resolution():
    key, info = ApplicationRegistry.resolve_app("calculadora")
    assert key == "calc"
    assert info["name"] == "Calculadora"

    key, info = ApplicationRegistry.resolve_app("spotify")
    assert key == "spotify"

    key, info = ApplicationRegistry.resolve_app("chrome")
    assert key == "chrome"

    key, info = ApplicationRegistry.resolve_app("aplicacion_fantasma_xyz")
    assert key is None
    assert info is None

def test_open_application_unauthorized():
    res = WindowsAutomationProvider.open_application("malware_trojan.exe")
    assert res["success"] is False
    assert res["error_code"] == "APP_NOT_ALLOWED"

def test_open_url_valid_and_invalid():
    res_valid = WindowsAutomationProvider.open_url("https://www.google.com")
    assert res_valid["success"] is True

    res_invalid_scheme = WindowsAutomationProvider.open_url("javascript:alert(1)")
    assert res_invalid_scheme["success"] is False
    assert res_invalid_scheme["error_code"] in ["BLOCKED_ACTION", "INVALID_URL"]

def test_path_access_validation():
    # Acceso a Desktop permitido
    is_safe, path, err = SecurityPolicy.validate_path_access("Desktop")
    assert is_safe is True
    assert path is not None

    # Path traversal bloqueado
    is_safe, path, err = SecurityPolicy.validate_path_access("../../Windows/System32/config/SAM")
    assert is_safe is False
    assert err == "BLOCKED_ACTION"

def test_action_classification():
    assert SecurityPolicy.classify_action("open_application", "chrome") == ActionRisk.SAFE
    assert SecurityPolicy.classify_action("open_url", "https://google.com") == ActionRisk.SAFE
    assert SecurityPolicy.classify_action("delete_file", "elimina este archivo") == ActionRisk.BLOCKED
    assert SecurityPolicy.classify_action("system_shutdown", "") == ActionRisk.CONFIRMATION_REQUIRED
    assert SecurityPolicy.classify_action("exec", "del /f /s C:\\Windows") == ActionRisk.BLOCKED

def test_active_application_query():
    info = WindowsAutomationProvider.get_active_application()
    assert isinstance(info, dict)
    assert "available" in info

def test_set_volume_functionality():
    # Nivel absoluto
    res_set = WindowsAutomationProvider.set_volume(level=30)
    assert res_set["success"] is True
    assert res_set["level"] == 30
    assert "30%" in res_set["message"]

    # Silenciar (mute)
    res_mute = WindowsAutomationProvider.set_volume(action="mute")
    assert res_mute["success"] is True
    assert res_mute["status"] == "MUTED"

    # Reactivar (unmute)
    res_unmute = WindowsAutomationProvider.set_volume(action="unmute")
    assert res_unmute["success"] is True
    assert res_unmute["status"] == "UNMUTED"

    # Delta relativo (+10, -10)
    res_up = WindowsAutomationProvider.set_volume(delta=10)
    assert res_up["success"] is True
    assert res_up["delta"] == 10

    res_down = WindowsAutomationProvider.set_volume(delta=-10)
    assert res_down["success"] is True
    assert res_down["delta"] == -10

    # Sin argumentos válidos
    res_invalid = WindowsAutomationProvider.set_volume()
    assert res_invalid["success"] is False
    assert res_invalid["status"] == "INVALID_ARGUMENTS"

def test_search_files_security_and_execution():
    # Consulta segura
    res_safe = WindowsAutomationProvider.search_files("documento_prueba_inexistente_123")
    assert res_safe["success"] is True
    assert "items" in res_safe

    # Consulta maliciosa con inyección de comandos
    res_injected = WindowsAutomationProvider.search_files("reporte & del /f C:\\Windows")
    assert res_injected["success"] is False
    assert res_injected["error_code"] == "BLOCKED_ACTION"

    # Consulta con patrón peligroso
    res_dangerous = WindowsAutomationProvider.search_files("rmdir /s /q System32")
    assert res_dangerous["success"] is False
    assert res_dangerous["error_code"] == "BLOCKED_ACTION"

def test_close_application_critical_process_protection():
    # Intento de cerrar proceso crítico del sistema
    res = WindowsAutomationProvider.close_application("explorer")
    # Si explorer estuviese mapeado o si se intenta un proceso crítico
    res_malware = WindowsAutomationProvider.close_application("cmd_malicioso")
    assert res_malware["success"] is False
    assert res_malware["status"] == "APP_NOT_ALLOWED"

