import platform
from enum import Enum
from typing import Tuple, Optional, Set
from core.config import settings
from core.logger import logger

class PlatformType(str, Enum):
    DESKTOP = "desktop"
    MOBILE = "mobile"
    WEB = "web"

class PlatformCapabilities:
    """
    Capa de capacidades de plataforma (Fase B.3).
    Distingue entre capacidades disponibles en entorno Desktop (Windows host nativo)
    y entornos móviles/web (PWA, Capacitor, cliente remoto).
    """

    DESKTOP_ONLY_TOOLS: Set[str] = {
        "open_url",
        "open_file",
        "open_folder",
        "focus_application",
        "get_active_application",
        "get_running_applications",
        "analyze_screen",
    }

    @classmethod
    def get_current_platform(cls) -> str:
        env = getattr(settings, "ENV", "desktop").lower()
        if env in ["mobile", "mobile-dev"]:
            return PlatformType.MOBILE.value
        elif env == "web":
            return PlatformType.WEB.value
        return PlatformType.DESKTOP.value

    @classmethod
    def is_desktop(cls) -> bool:
        return cls.get_current_platform() == PlatformType.DESKTOP.value and platform.system() == "Windows"

    @classmethod
    def is_tool_supported(cls, tool_name: str, target_platform: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        plat = target_platform or cls.get_current_platform()
        if tool_name in cls.DESKTOP_ONLY_TOOLS:
            if plat != PlatformType.DESKTOP.value or platform.system() != "Windows":
                msg = (
                    f"La herramienta '{tool_name}' solo está disponible en la versión de escritorio de Windows (Desktop). "
                    f"En plataformas {plat.upper()} esta acción no es compatible directamente."
                )
                logger.warning(f"[PlatformCapabilities] Bloqueada '{tool_name}' por incompatibilidad de plataforma ({plat}).")
                return False, msg
        return True, None
