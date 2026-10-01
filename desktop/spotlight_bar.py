import sys
import json
import urllib.request
import urllib.parse
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, 
    QPushButton, QGraphicsDropShadowEffect, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QSize, QTimer
from PyQt6.QtGui import QColor, QFont, QIcon, QPixmap, QPainter, QBrush, QPen

class SpotlightWindow(QWidget):
    """
    Ventana flotante de interacción rápida al estilo Spotlight / Raycast para JARVIS.
    - Se activa/oculta globalmente con Alt + Espacio.
    - Barra de entrada de texto limpia con ejecución inmediata de comandos.
    - Visualización rápida de respuestas y badges de acción.
    - Cierre instantáneo con la tecla Escape.
    """
    toggle_requested = pyqtSignal()
    open_full_requested = pyqtSignal()

    def __init__(self, api_base_url="http://127.0.0.1:5001", parent=None):
        super().__init__(parent)
        self.api_base_url = api_base_url
        self._drag_pos = QPoint()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(680)

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(0)

        # Contenedor con efecto Glassmorphic / Obsidian
        self.container = QFrame(self)
        self.container.setObjectName("spotlightContainer")
        self.container.setStyleSheet("""
            QFrame#spotlightContainer {
                background-color: rgba(10, 17, 24, 0.94);
                border: 1.5px solid rgba(0, 242, 254, 0.45);
                border-radius: 18px;
            }
        """)

        # Sombra suave
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(35)
        shadow.setColor(QColor(0, 242, 254, 45))
        shadow.setOffset(0, 8)
        self.container.setGraphicsEffect(shadow)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(18, 16, 18, 16)
        container_layout.setSpacing(12)

        # Fila superior: Input de búsqueda
        search_row = QHBoxLayout()
        search_row.setSpacing(12)

        # Orbe / Logo indicador
        self.logo_label = QLabel("⚡", self)
        self.logo_label.setStyleSheet("font-size: 20px; color: #00F2FE;")
        search_row.addWidget(self.logo_label)

        # Campo de entrada
        self.input_edit = QLineEdit(self)
        self.input_edit.setPlaceholderText("¿En qué te ayudo, Dante? (ej. abre Chrome, pon música, recuerda...)")
        self.input_edit.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: #E6F8FF;
                font-family: 'Segoe UI', system-ui, sans-serif;
                font-size: 16px;
                font-weight: 500;
                selection-background-color: #00F2FE;
                selection-color: #0A1118;
            }
            QLineEdit::placeholder {
                color: rgba(230, 248, 255, 0.4);
                font-style: normal;
            }
        """)
        self.input_edit.returnPressed.connect(self._handle_submit)
        search_row.addWidget(self.input_edit)

        # Botón para abrir ventana completa
        self.btn_full = QPushButton("Abrir App", self)
        self.btn_full.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_full.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 242, 254, 0.12);
                color: #00F2FE;
                border: 1px solid rgba(0, 242, 254, 0.35);
                border-radius: 8px;
                padding: 5px 12px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(0, 242, 254, 0.25);
                color: #FFFFFF;
                border-color: #00F2FE;
            }
        """)
        self.btn_full.clicked.connect(self._on_open_full)
        search_row.addWidget(self.btn_full)

        container_layout.addLayout(search_row)

        # Línea divisoria
        self.divider = QFrame()
        self.divider.setFrameShape(QFrame.Shape.HLine)
        self.divider.setStyleSheet("background-color: rgba(0, 242, 254, 0.2); max-height: 1px;")
        self.divider.hide()
        container_layout.addWidget(self.divider)

        # Área de respuesta / feedback
        self.response_area = QFrame()
        self.response_area.hide()
        resp_layout = QVBoxLayout(self.response_area)
        resp_layout.setContentsMargins(0, 4, 0, 4)
        resp_layout.setSpacing(8)

        self.response_label = QLabel("")
        self.response_label.setWordWrap(True)
        self.response_label.setStyleSheet("""
            color: #FAF5EE;
            font-size: 14px;
            line-height: 1.5;
            font-family: 'Segoe UI', system-ui, sans-serif;
        """)
        resp_layout.addWidget(self.response_label)

        # Barra inferior de estado / acciones rápidas
        self.bottom_bar = QHBoxLayout()
        self.action_badge = QLabel("")
        self.action_badge.setStyleSheet("""
            background-color: rgba(46, 125, 50, 0.25);
            color: #81C784;
            border: 1px solid rgba(129, 199, 132, 0.3);
            border-radius: 6px;
            padding: 3px 8px;
            font-size: 11px;
            font-weight: bold;
        """)
        self.action_badge.hide()
        self.bottom_bar.addWidget(self.action_badge)

        self.bottom_bar.addStretch()

        self.hint_label = QLabel("Esc para cerrar  •  Enter para consultar", self)
        self.hint_label.setStyleSheet("color: rgba(250, 245, 238, 0.35); font-size: 11px;")
        self.bottom_bar.addWidget(self.hint_label)

        resp_layout.addLayout(self.bottom_bar)
        container_layout.addWidget(self.response_area)

        main_layout.addWidget(self.container)

    def show_spotlight(self):
        """Muestra y posiciona la ventana centrada horizontalmente en el tercio superior."""
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = int(screen.height() * 0.18)
        self.move(x, y)
        self.show()
        self.raise_()
        self.activateWindow()
        self.input_edit.setFocus()
        self.input_edit.selectAll()

    def toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show_spotlight()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
        else:
            super().keyPressEvent(event)

    def _handle_submit(self):
        text = self.input_edit.text().strip()
        if not text:
            return

        self.divider.show()
        self.response_area.show()
        self.response_label.setText("⚡ Pensando...")
        self.action_badge.hide()
        self.input_edit.setEnabled(False)

        # Enviar petición a FastAPI de forma asíncrona mediante QTimer
        QTimer.singleShot(50, lambda: self._query_jarvis(text))

    def _query_jarvis(self, prompt: str):
        try:
            req_data = json.dumps({"prompt": prompt}).encode("utf-8")
            req = urllib.request.Request(
                f"{self.api_base_url}/api/chat",
                data=req_data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.status == 200:
                    res_json = json.loads(response.read().decode("utf-8"))
                    data = res_json.get("data") if (isinstance(res_json, dict) and res_json.get("ok") and "data" in res_json) else res_json
                    answer = data.get("text", "Comando ejecutado.")
                    self.response_label.setText(answer)
                    
                    # Mostrar badge de acción si se ejecutó alguna tool
                    tools = data.get("tools_executed", [])
                    action_type = data.get("action_type")
                    if tools:
                        self.action_badge.setText(f"✓ {tools[0]}")
                        self.action_badge.show()
                    elif action_type:
                        self.action_badge.setText(f"✓ {action_type}")
                        self.action_badge.show()
                else:
                    self.response_label.setText("Error en la respuesta del asistente.")
        except Exception as e:
            self.response_label.setText(f"Error de conexión con JARVIS: {e}")
        finally:
            self.input_edit.setEnabled(True)
            self.input_edit.setFocus()
            self.input_edit.selectAll()

    def _on_open_full(self):
        self.hide()
        self.open_full_requested.emit()
