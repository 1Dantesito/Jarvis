from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMessageBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent
from desktop.tray_icon import create_jarvis_icon

class MainWindow(QMainWindow):
    """
    Ventana principal nativa de escritorio para JARVIS (PyQt6 + WebEngine).
    - Incrusta la interfaz visual completa de FastAPI/WebSockets.
    - Se minimiza a la bandeja del sistema (System Tray) al presionar cerrar (X).
    """
    closing_to_tray = pyqtSignal()

    def __init__(self, server_url="http://127.0.0.1:5001", parent=None):
        super().__init__(parent)
        self.server_url = server_url
        self.force_close = False

        self.setWindowTitle("JARVIS — Asistente Personal de Escritorio")
        self.setWindowIcon(create_jarvis_icon())
        self.resize(1240, 840)
        self.setMinimumSize(960, 640)

        self._init_ui()

    def _init_ui(self):
        self.web_view = QWebEngineView(self)
        self.web_view.setUrl(QUrl(self.server_url))
        self.setCentralWidget(self.web_view)

    def show_and_focus(self):
        """Restaura y trae la ventana al frente con foco."""
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event: QCloseEvent):
        """
        Intercepta el botón de cerrar (X) para minimizar a la bandeja en lugar de terminar el proceso.
        """
        if self.force_close:
            event.accept()
        else:
            event.ignore()
            self.hide()
            self.closing_to_tray.emit()
