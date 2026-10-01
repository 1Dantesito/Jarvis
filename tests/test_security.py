import pytest
from core.security import SecurityPolicy, ActionRisk

def test_safe_apps_whitelist():
    is_safe, canonical, cmd = SecurityPolicy.validate_app("calculadora")
    assert is_safe is True
    assert canonical in ["calc", "calculadora"]

    is_safe_chrome, can_chrome, _ = SecurityPolicy.validate_app("chrome")
    assert is_safe_chrome is True

    is_safe_bad, _, _ = SecurityPolicy.validate_app("malware_unknown_app")
    assert is_safe_bad is False

def test_dangerous_commands():
    assert SecurityPolicy.is_dangerous("del /f /s C:/Windows") is True
    assert SecurityPolicy.is_dangerous("rmdir /s /q System32") is True
    assert SecurityPolicy.is_dangerous("echo Hola") is False

def test_evasion_variations_case_and_spaces():
    """Prueba que variaciones de mayúsculas y espacios múltiples no burlen el filtro."""
    assert SecurityPolicy.is_dangerous("DEL   /F   /Q C:\\") is True
    assert SecurityPolicy.is_dangerous("rMdIr   /S   /Q") is True
    assert SecurityPolicy.is_dangerous("ShUtDoWn  -s -t 0") is True
    assert SecurityPolicy.is_dangerous("PoWeRsHeLl  -c  remove") is True
    assert SecurityPolicy.is_dangerous("powershell   -enc   dGVzdA==") is True

def test_command_chaining_and_injection():
    """Prueba que concatenación de comandos (&, &&, ;, |, ||) resulte en BLOCKED."""
    assert SecurityPolicy.classify_action("open_application", "chrome & del /f") == ActionRisk.BLOCKED
    assert SecurityPolicy.classify_action("open_application", "calc.exe; shutdown") == ActionRisk.BLOCKED
    assert SecurityPolicy.classify_action("open_url", "https://google.com | rmdir /s") == ActionRisk.BLOCKED
    assert SecurityPolicy.classify_action("open_file", "test.txt`whoami`") == ActionRisk.BLOCKED
    assert SecurityPolicy.classify_action("open_file", "test.txt$(whoami)") == ActionRisk.BLOCKED

def test_allowlist_fail_closed_default():
    """Prueba que cualquier acción no explícitamente autorizada sea denegada (BLOCKED por defecto)."""
    assert SecurityPolicy.classify_action("unknown_action_xyz", "some_target") == ActionRisk.BLOCKED
    assert SecurityPolicy.classify_action("run_shell", "dir") == ActionRisk.BLOCKED
    assert SecurityPolicy.classify_action("execute_script", "script.py") == ActionRisk.BLOCKED
    assert SecurityPolicy.classify_action("download_payload", "http://evil.com") == ActionRisk.BLOCKED
    assert SecurityPolicy.classify_action("arbitrary_execution", "") == ActionRisk.BLOCKED

def test_blocked_file_actions_strictly_blocked():
    """Prueba que BLOCKED_FILE_ACTIONS devuelva siempre BLOCKED."""
    assert SecurityPolicy.classify_action("delete_file", "reporte.docx") == ActionRisk.BLOCKED
    assert SecurityPolicy.classify_action("remove_file", "nota.txt") == ActionRisk.BLOCKED
    assert SecurityPolicy.classify_action("delete_folder", "Carpeta") == ActionRisk.BLOCKED
    assert SecurityPolicy.classify_action("unlink", "archivo.tmp") == ActionRisk.BLOCKED

def test_safe_actions_allowlist():
    """Prueba que solo las acciones seguras explícitas devuelvan SAFE si sus argumentos son limpios."""
    assert SecurityPolicy.classify_action("open_application", "chrome") == ActionRisk.SAFE
    assert SecurityPolicy.classify_action("create_text_file", "nota.txt") == ActionRisk.SAFE
    assert SecurityPolicy.classify_action("read_text_file", "nota.txt") == ActionRisk.SAFE
    assert SecurityPolicy.classify_action("search_files", "tesis") == ActionRisk.SAFE
    assert SecurityPolicy.classify_action("list_files", "Desktop") == ActionRisk.SAFE

def test_destructive_actions_require_confirmation():
    """Prueba que operaciones masivas destructivas exijan CONFIRMATION_REQUIRED."""
    assert SecurityPolicy.classify_action("clear_memory") == ActionRisk.CONFIRMATION_REQUIRED
    assert SecurityPolicy.classify_action("clear_all_reminders") == ActionRisk.CONFIRMATION_REQUIRED
    assert SecurityPolicy.classify_action("clear_all_tasks") == ActionRisk.CONFIRMATION_REQUIRED

