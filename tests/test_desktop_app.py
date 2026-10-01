import sys
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QCloseEvent

from desktop.tray_icon import create_jarvis_icon, JarvisTrayIcon
from desktop.spotlight_bar import SpotlightWindow
from desktop.main_window import MainWindow
from desktop.app import HotkeyBridge, is_port_in_use

@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    yield app

def test_jarvis_icon_creation(qapp):
    icon = create_jarvis_icon(64)
    assert isinstance(icon, QIcon)
    assert not icon.isNull()

def test_spotlight_window_properties(qapp):
    spotlight = SpotlightWindow()
    flags = spotlight.windowFlags()
    assert bool(flags & Qt.WindowType.FramelessWindowHint) is True
    assert bool(flags & Qt.WindowType.WindowStaysOnTopHint) is True
    assert bool(flags & Qt.WindowType.Tool) is True

    # Comprobar toggle y show
    spotlight.show_spotlight()
    assert spotlight.isVisible() is True
    spotlight.toggle()
    assert spotlight.isVisible() is False
    spotlight.close()

def test_tray_icon_menu_actions(qapp):
    tray = JarvisTrayIcon()
    assert tray.icon() is not None
    menu = tray.contextMenu()
    assert menu is not None
    action_texts = [a.text() for a in menu.actions()]
    assert any("Abrir JARVIS" in t for t in action_texts)
    assert any("Barra Rápida" in t for t in action_texts)
    assert any("Salir de JARVIS" in t for t in action_texts)

def test_main_window_minimizes_to_tray_on_close(qapp):
    window = MainWindow()
    minimized_signal_received = False

    def on_closing():
        nonlocal minimized_signal_received
        minimized_signal_received = True

    window.closing_to_tray.connect(on_closing)
    window.show()
    assert window.isVisible() is True

    # Simular evento de cierre por el usuario
    close_event = QCloseEvent()
    window.closeEvent(close_event)

    # Debe ser ignorado (minimizado a bandeja) y emitir señal
    assert not close_event.isAccepted()
    assert minimized_signal_received is True
    assert window.isVisible() is False

    # Forzar cierre para limpieza
    window.force_close = True
    window.close()

def test_hotkey_bridge_signal(qapp):
    bridge = HotkeyBridge()
    received = False

    def on_hotkey():
        nonlocal received
        received = True

    bridge.hotkey_pressed.connect(on_hotkey)
    bridge.hotkey_pressed.emit()
    assert received is True

def test_port_check_function():
    # Probar chequeo de puerto en un puerto inexistente
    in_use = is_port_in_use(59999)
    assert isinstance(in_use, bool)
