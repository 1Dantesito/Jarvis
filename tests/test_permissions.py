import pytest
from core.permissions import PermissionManager, PermissionCategory, PermissionState

def test_permissions_default_state():
    perms = PermissionManager.get_all_permissions()
    assert perms["MICROPHONE"] == "GRANTED"
    assert perms["FILES"] == "GRANTED"
    assert perms["AUTOMATION"] == "GRANTED"

def test_permissions_override():
    PermissionManager.set_permission(PermissionCategory.AUTOMATION, PermissionState.DENIED)
    assert PermissionManager.is_granted(PermissionCategory.AUTOMATION) is False

    # Restaurar
    PermissionManager.set_permission(PermissionCategory.AUTOMATION, PermissionState.GRANTED)
    assert PermissionManager.is_granted(PermissionCategory.AUTOMATION) is True

@pytest.mark.asyncio
async def test_tools_enforce_permission_manager():
    from tools.implementations.system_tools import LocationTool, SetVolumeTool
    from tools.implementations.reminder_tools import CreateReminderTool

    # 1. LocationTool
    try:
        PermissionManager.set_permission(PermissionCategory.LOCATION, PermissionState.DENIED)
        loc_res = await LocationTool().execute()
        assert loc_res["success"] is False
        assert "Permiso denegado" in loc_res["error"]
        assert "LOCATION" in loc_res["error"]
    finally:
        PermissionManager.set_permission(PermissionCategory.LOCATION, PermissionState.GRANTED)

    # 2. SetVolumeTool
    try:
        PermissionManager.set_permission(PermissionCategory.AUTOMATION, PermissionState.DENIED)
        vol_res = await SetVolumeTool().execute(level=50)
        assert vol_res["success"] is False
        assert "Permiso denegado" in vol_res["error"]
        assert "AUTOMATION" in vol_res["error"]
    finally:
        PermissionManager.set_permission(PermissionCategory.AUTOMATION, PermissionState.GRANTED)

    # 3. CreateReminderTool
    try:
        PermissionManager.set_permission(PermissionCategory.NOTIFICATIONS, PermissionState.DENIED)
        rem_res = await CreateReminderTool().execute(title="Test", remind_at="en 10 minutos")
        assert rem_res["success"] is False
        assert "Permiso denegado" in rem_res["error"]
        assert "NOTIFICATIONS" in rem_res["error"]
    finally:
        PermissionManager.set_permission(PermissionCategory.NOTIFICATIONS, PermissionState.GRANTED)
