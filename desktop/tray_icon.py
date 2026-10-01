import os
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen
from PyQt6.QtCore import Qt, pyqtSignal

def create_jarvis_icon(size=64) -> QIcon:
    """Genera o carga el icono nativo de JARVIS (Liquid Glass / Arc Reactor)."""
    ico_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "jarvis.ico")
    if os.path.exists(ico_path):
        icon = QIcon(ico_path)
        if not icon.isNull():
            return icon

    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Círculo base (Obsidian Glass)
    painter.setBrush(QBrush(QColor(10, 17, 24)))
    painter.setPen(QPen(QColor(0, 242, 254, 200), 2))
    painter.drawEllipse(4, 4, size - 8, size - 8)

    # Anillo interior cian neón
    painter.setPen(QPen(QColor(79, 172, 254, 220), 2))
    painter.drawEllipse(12, 12, size - 24, size - 24)

    # Núcleo energético central
    painter.setBrush(QBrush(QColor(0, 242, 254)))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(size // 2 - 5, size // 2 - 5, 10, 10)

    painter.end()
    return QIcon(pixmap)

class JarvisTrayIcon(QSystemTrayIcon):
    """
    Bandeja del sistema (System Tray) para JARVIS:
    - Permite minimizar la ventana a la bandeja sin interrumpir la ejecución.
    - Menú contextual con accesos directos rápidos y salida limpia.
    """
    show_main_requested = pyqtSignal()
    toggle_spotlight_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(create_jarvis_icon())
        self.setToolTip("JARVIS — Asistente de Escritorio Activo (Alt + Espacio)")

        self._init_menu()
        self.activated.connect(self._on_activated)

    def _init_menu(self):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #0A1118;
                color: #E6F8FF;
                border: 1px solid rgba(0, 242, 254, 0.4);
                border-radius: 8px;
                padding: 6px;
                font-family: 'Segoe UI', system-ui, sans-serif;
                font-size: 13px;
            }
            QMenu::item {
                padding: 6px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: rgba(0, 242, 254, 0.2);
                color: #00F2FE;
                font-weight: 600;
            }
            QMenu::separator {
                height: 1px;
                background-color: rgba(0, 242, 254, 0.2);
                margin: 4px 8px;
            }
        """)

        action_show = menu.addAction("Abrir JARVIS")
        action_show.triggered.connect(self.show_main_requested.emit)

        action_spotlight = menu.addAction("Barra Rápida (Alt + Espacio)")
        action_spotlight.triggered.connect(self.toggle_spotlight_requested.emit)

        menu.addSeparator()

        action_status = menu.addAction("● En línea (Localhost:5001)")
        action_status.setEnabled(False)

        menu.addSeparator()

        action_quit = menu.addAction("Salir de JARVIS")
        action_quit.triggered.connect(self.quit_requested.emit)

        self.setContextMenu(menu)

    def _on_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.show_main_requested.emit()
