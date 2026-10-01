import re
import time
from typing import Optional, Tuple
from enum import Enum
from core.logger import logger

class ConversationState(str, Enum):
    BACKGROUND = "background"       # solo escuchando wake word
    ACTIVE = "active"                # ventana abierta, todo se procesa como comando
    PROCESSING = "processing"        # transcribiendo / LLM pensando
    RESPONDING = "responding"        # Jarvis está hablando (TTS)

class WakeWordDetector:
    """
    Detector de palabra de activación local y gestor de ventana de conversación.
    Permite activar JARVIS con 'Jarvis', 'Oye Jarvis', 'Hey Jarvis' y sostener
    conversaciones fluidas multiturno sin repetir la palabra clave en cada frase.
    """
    
    WAKE_REGEX = re.compile(r"(?:oye|hola|hey|ok)?\s*,?\s*jarvis\b", re.IGNORECASE)

    def __init__(self, keyword: str = "jarvis", threshold: float = 0.5, window_seconds: int = 12):
        self.keyword = keyword.lower()
        self.threshold = threshold
        self.window_seconds = window_seconds
        self.state = ConversationState.BACKGROUND
        self.last_turn_timestamp: float = 0.0

    def detect_wake_word(self, transcript: str) -> bool:
        if not transcript or not transcript.strip():
            return False
        return bool(self.WAKE_REGEX.search(transcript.strip()))

    def extract_command(self, transcript: str) -> Tuple[bool, str]:
        """
        Extrae el comando útil eliminando el prefijo de la palabra de activación.
        Ejemplo: 'Oye Jarvis, pon música de rock' -> (True, 'pon música de rock')
        """
        if not transcript or not transcript.strip():
            return False, ""

        clean = transcript.strip()
        if self.WAKE_REGEX.search(clean):
            cmd = self.WAKE_REGEX.sub("", clean, count=1).strip()
            cmd = re.sub(r"^[,:\s.-]+", "", cmd).strip()
            return True, cmd

        return False, clean

    def check_window_expiration(self) -> bool:
        """
        Comprueba si la ventana de conversación de N segundos ha expirado.
        """
        if self.state == ConversationState.ACTIVE:
            elapsed = time.time() - self.last_turn_timestamp
            if elapsed > self.window_seconds:
                logger.info(f"[WakeWordDetector] Ventana de conversación expirada ({elapsed:.1f}s sin actividad). Regresando a BACKGROUND.")
                self.state = ConversationState.BACKGROUND
                return True
        return False

    def touch_turn(self):
        """Reinicia el temporizador de la ventana activa tras cada turno."""
        self.last_turn_timestamp = time.time()

    def process_incoming_speech(self, transcript: str) -> Tuple[bool, str]:
        """
        Evalúa si la frase debe procesarse según el estado actual:
        - Si está en BACKGROUND: solo se activa si contiene la wake word.
        - Si está en ACTIVE: procesa la frase directamente.
        Retorna: (should_process, command_to_execute)
        """
        self.check_window_expiration()
        clean = transcript.strip()
        if not clean:
            return False, ""

        has_wake, extracted_cmd = self.extract_command(clean)

        if self.state == ConversationState.BACKGROUND:
            if has_wake:
                self.state = ConversationState.ACTIVE
                self.touch_turn()
                logger.info(f"[WakeWordDetector] Wake word detectada. Transición a ACTIVE. Comando: '{extracted_cmd}'")
                return True, extracted_cmd
            # Ruido de fondo / TV / otra persona -> ignorar en silencio
            return False, ""
        else:
            # Estado ACTIVE: dentro de la ventana de conversación
            self.touch_turn()
            cmd = extracted_cmd if has_wake else clean
            logger.info(f"[WakeWordDetector] En ventana ACTIVE. Procesando turno: '{cmd}'")
            return True, cmd
