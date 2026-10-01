import sys
import time
import socket
import threading
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from pynput import keyboard

from desktop.main_window import MainWindow
from desktop.spotlight_bar import SpotlightWindow
from desktop.tray_icon import JarvisTrayIcon

class HotkeyBridge(QObject):
    """Puente seguro entre el hilo de pynput y el hilo de interfaz gráfica de Qt."""
    hotkey_pressed = pyqtSignal()

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Verifica si el puerto del backend ya está ocupado."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

def start_backend_server_thread(host="127.0.0.1", port=5001):
    """Inicia el servidor uvicorn en segundo plano si no está en ejecución."""
    import uvicorn
    from api.server import app

    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="warning",
        access_log=False
    )
    server = uvicorn.Server(config)
    
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    return server, thread

class JarvisDesktopApplication:
    """
    Controlador principal de la aplicación de escritorio nativa de JARVIS.
    Coordina:
    - Servidor FastAPI backend.
    - Ventana principal con interfaz WebEngine.
    - Barra flotante rápida estilo Spotlight/Raycast (Alt + Espacio).
    - Minimización continua a la bandeja del sistema (System Tray).
    """

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setApplicationName("JARVIS Assistant")

        self.server_host = "127.0.0.1"
        self.server_port = 5001
        self.server_url = f"http://{self.server_host}:{self.server_port}"
        self.uvicorn_server = None

        # 1. Iniciar servidor backend si no está activo
        if not is_port_in_use(self.server_port, self.server_host):
            self.uvicorn_server, _ = start_backend_server_thread(self.server_host, self.server_port)
            # Espera activa ultra rápida para enlace de sockets
            for _ in range(60):
                if is_port_in_use(self.server_port, self.server_host):
                    break
                time.sleep(0.05)

        # 2. Inicializar Ventana Principal, Spotlight y Bandeja
        self.main_window = MainWindow(server_url=self.server_url)
        self.spotlight = SpotlightWindow(api_base_url=self.server_url)
        self.tray = JarvisTrayIcon()

        # 3. Conexión de Señales y Eventos
        self.tray.show_main_requested.connect(self.main_window.show_and_focus)
        self.tray.toggle_spotlight_requested.connect(self.spotlight.toggle)
        self.tray.quit_requested.connect(self.quit)
        self.main_window.closing_to_tray.connect(self._on_minimized_to_tray)
        self.spotlight.open_full_requested.connect(self.main_window.show_and_focus)

        # 4. Configuración de Atajo Global (Alt + Espacio)
        self.hotkey_bridge = HotkeyBridge()
        self.hotkey_bridge.hotkey_pressed.connect(self.spotlight.toggle)

        self.hotkey_listener = keyboard.GlobalHotKeys({
            '<alt>+<space>': lambda: self.hotkey_bridge.hotkey_pressed.emit()
        })
        self.hotkey_listener.daemon = True
        self.hotkey_listener.start()

    def _on_minimized_to_tray(self):
        self.tray.showMessage(
            "JARVIS",
            "La aplicación continúa ejecutándose en segundo plano.\nPresiona Alt + Espacio para la barra rápida.",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )

    def run(self, start_minimized: bool = False):
        """Ejecuta el bucle de eventos de la aplicación."""
        self.tray.show()
        if not start_minimized:
            self.main_window.show_and_focus()

        return self.app.exec()

    def quit(self):
        """Cierre ordenado de listeners, servidor y ventanas."""
        try:
            if self.hotkey_listener and self.hotkey_listener.is_alive():
                self.hotkey_listener.stop()
        except Exception:
            pass

        self.main_window.force_close = True
        self.main_window.close()
        self.spotlight.close()
        self.tray.hide()

        if self.uvicorn_server:
            self.uvicorn_server.should_exit = True

        self.app.quit()

def run_desktop_app():
    desktop_app = JarvisDesktopApplication()
    sys.exit(desktop_app.run())

if __name__ == "__main__":
    run_desktop_app()
