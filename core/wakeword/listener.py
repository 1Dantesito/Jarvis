import time
import threading
from collections import deque
from typing import Optional, Callable, Dict, Any, List
from core.logger import logger
from core.permissions import PermissionManager, PermissionCategory
from core.platform_capabilities import PlatformCapabilities
from .detector import WakeWordDetector, ConversationState

class BackgroundWakeWordListener:
    """
    Motor de escucha de wake-word en segundo plano para entorno Desktop (Fase 14).
    Ejecuta un bucle en hilo dedicado con buffer circular de bajo consumo (<2% CPU).
    Detecta la palabra de activación 'Jarvis' o frases equivalentes y dispara un callback.
    """

    def __init__(
        self,
        keyword: str = "jarvis",
        on_wake_callback: Optional[Callable[[str], None]] = None,
        buffer_size: int = 100
    ):
        self.detector = WakeWordDetector(keyword=keyword, window_seconds=10)
        self.on_wake_callback = on_wake_callback
        self.audio_buffer = deque(maxlen=buffer_size)
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._text_queue = deque(maxlen=50)

    @property
    def is_running(self) -> bool:
        return self._running

    def start(self) -> bool:
        if not PlatformCapabilities.is_desktop():
            logger.info("[WakeWordListener] Omitido: disponible únicamente en entorno Desktop.")
            return False

        if not PermissionManager.is_granted(PermissionCategory.MICROPHONE):
            logger.warning("[WakeWordListener] Permiso de micrófono denegado en PermissionManager.")
            return False

        if self._running:
            return True

        self._stop_event.clear()
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="JarvisWakeWordWorker")
        self._thread.start()
        logger.info("[WakeWordListener] Hilo de detección de wake-word iniciado en segundo plano.")
        return True

    def stop(self):
        if not self._running:
            return
        self._stop_event.set()
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        logger.info("[WakeWordListener] Hilo de detección de wake-word detenido.")

    def feed_transcript(self, transcript: str):
        """Alimenta texto reconocido hacia la cola circular para evaluación."""
        if transcript and transcript.strip():
            self._text_queue.append(transcript.strip())

    def _loop(self):
        while not self._stop_event.is_set():
            try:
                # Comprobar expiración periódica de la ventana
                self.detector.check_window_expiration()

                # Procesar frases acumuladas en la cola
                while self._text_queue and not self._stop_event.is_set():
                    phrase = self._text_queue.popleft()
                    should_process, command = self.detector.process_incoming_speech(phrase)
                    if should_process and self.on_wake_callback:
                        logger.info(f"[WakeWordListener] Disparando callback con comando: '{command}'")
                        try:
                            self.on_wake_callback(command)
                        except Exception as cb_err:
                            logger.error(f"[WakeWordListener] Error en callback de wake word: {cb_err}")

                # Dormir 50ms para mantener consumo de CPU < 2%
                time.sleep(0.05)
            except Exception as e:
                logger.error(f"[WakeWordListener] Excepción en bucle de escucha: {e}")
                time.sleep(0.2)
