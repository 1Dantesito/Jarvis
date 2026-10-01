from enum import Enum
from typing import Dict, Any
from core.system_capabilities import SystemCapabilities

class PermissionState(str, Enum):
    GRANTED = "GRANTED"
    DENIED = "DENIED"
    NOT_REQUIRED = "NOT_REQUIRED"
    UNKNOWN = "UNKNOWN"

class PermissionCategory(str, Enum):
    MICROPHONE = "MICROPHONE"
    LOCATION = "LOCATION"
    NOTIFICATIONS = "NOTIFICATIONS"
    FILES = "FILES"
    AUTOMATION = "AUTOMATION"
    CALENDAR = "CALENDAR"

class PermissionManager:
    """
    Control central que distingue entre:
    1. Permiso lógico (autorización de Dante).
    2. Capacidad física/sistema (si el hardware/SO realmente lo soporta en este instante).
    """
    _permissions = {
        PermissionCategory.MICROPHONE: PermissionState.GRANTED,
        PermissionCategory.LOCATION: PermissionState.GRANTED,
        PermissionCategory.NOTIFICATIONS: PermissionState.GRANTED,
        PermissionCategory.FILES: PermissionState.GRANTED,
        PermissionCategory.AUTOMATION: PermissionState.GRANTED,
        PermissionCategory.CALENDAR: PermissionState.NOT_REQUIRED
    }

    @classmethod
    def check_permission(cls, category: PermissionCategory) -> PermissionState:
        return cls._permissions.get(category, PermissionState.UNKNOWN)

    @classmethod
    def is_granted(cls, category: PermissionCategory) -> bool:
        return cls.check_permission(category) == PermissionState.GRANTED

    @classmethod
    def set_permission(cls, category: PermissionCategory, state: PermissionState):
        cls._permissions[category] = state

    @classmethod
    def get_all_permissions(cls) -> Dict[str, str]:
        return {cat.value: state.value for cat, state in cls._permissions.items()}

    @classmethod
    def get_effective_matrix(cls) -> Dict[str, Dict[str, Any]]:
        """
        Retorna la matriz combinada de Permiso Lógico vs Capacidad Real del Sistema.
        """
        env = SystemCapabilities.get_full_environmental_status()
        
        return {
            "microphone": {
                "user_permission": cls.check_permission(PermissionCategory.MICROPHONE).value,
                "system_capability": env["microphone"],
                "is_operational": cls.is_granted(PermissionCategory.MICROPHONE) and env["microphone_available"]
            },
            "location": {
                "user_permission": cls.check_permission(PermissionCategory.LOCATION).value,
                "system_capability": env["connectivity"],
                "is_operational": cls.is_granted(PermissionCategory.LOCATION) and env["is_online"]
            },
            "notifications": {
                "user_permission": cls.check_permission(PermissionCategory.NOTIFICATIONS).value,
                "system_capability": env["notifications"],
                "is_operational": cls.is_granted(PermissionCategory.NOTIFICATIONS)
            },
            "files": {
                "user_permission": cls.check_permission(PermissionCategory.FILES).value,
                "system_capability": "Carpetas de usuario accesibles",
                "is_operational": cls.is_granted(PermissionCategory.FILES)
            },
            "automation": {
                "user_permission": cls.check_permission(PermissionCategory.AUTOMATION).value,
                "system_capability": f"Windows ({env['os']})",
                "is_operational": cls.is_granted(PermissionCategory.AUTOMATION)
            }
        }
