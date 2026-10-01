import ctypes
import socket
import platform
import psutil
from typing import Dict, Any, Optional
from core.logger import logger

class SystemCapabilities:
    """
    Sondas reales del hardware y sistema operativo Windows.
    Comprueba capacidades físicas reales independientemente de los permisos lógicos.
    """

    @classmethod
    def check_internet_connectivity(cls, host: str = "8.8.8.8", port: int = 53, timeout: float = 0.6) -> bool:
        try:
            socket.create_connection((host, port), timeout=timeout)
            return True
        except Exception:
            return False

    @classmethod
    def get_microphone_status(cls) -> Dict[str, Any]:
        """
        Consulta la disponibilidad real de dispositivos de entrada de audio en Windows.
        """
        try:
            num_devs = ctypes.windll.winmm.waveInGetNumDevs()
            if num_devs > 0:
                return {
                    "available": True,
                    "devices_count": num_devs,
                    "status_text": f"Disponible ({num_devs} dispositivos detectados)"
                }
            return {
                "available": False,
                "devices_count": 0,
                "status_text": "No se detectaron micrófonos"
            }
        except Exception as e:
            return {
                "available": False,
                "devices_count": 0,
                "status_text": f"Error consultando audio: {e}"
            }

    @classmethod
    def get_os_info(cls) -> Dict[str, str]:
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine()
        }

    @classmethod
    def get_active_window_info(cls) -> Dict[str, Any]:
        """
        Obtiene la ventana y aplicación actualmente en primer plano.
        """
        try:
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return {"available": False, "process": "Desconocido", "title": "Sin ventana activa"}

            length = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value.strip()

            pid = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            proc_name = "Desconocido"
            try:
                p = psutil.Process(pid.value)
                proc_name = p.name()
            except Exception:
                pass

            return {
                "available": bool(title or proc_name != "Desconocido"),
                "process": proc_name,
                "title": title or proc_name
            }
        except Exception:
            return {"available": False, "process": "Desconocido", "title": "Sin ventana activa"}

    @classmethod
    def get_full_environmental_status(cls) -> Dict[str, Any]:
        is_online = cls.check_internet_connectivity()
        mic = cls.get_microphone_status()
        os_info = cls.get_os_info()
        win = cls.get_active_window_info()

        return {
            "connectivity": "Online" if is_online else "Offline",
            "is_online": is_online,
            "microphone": mic["status_text"],
            "microphone_available": mic["available"],
            "os": f"{os_info['system']} {os_info['release']}",
            "active_app": win["process"],
            "active_window": win["title"],
            "notifications": "Disponibles (Windows Toast)"
        }
