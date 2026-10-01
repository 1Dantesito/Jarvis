from enum import Enum
from typing import Optional, Callable, List
from core.logger import logger

class VoiceState(str, Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    SPEAKING = "SPEAKING"
    PROCESSING = "PROCESSING"
    INTERRUPTED = "INTERRUPTED"
    ERROR = "ERROR"

class VoiceStateMachine:
    """
    Máquina de estados estricta con seguimiento de generation_id para prevención
    absoluta de Race Conditions en reproducción de audio y Barge-in.
    """
    
    ALLOWED_TRANSITIONS = {
        VoiceState.IDLE: [VoiceState.LISTENING, VoiceState.PROCESSING, VoiceState.ERROR],
        VoiceState.LISTENING: [VoiceState.PROCESSING, VoiceState.IDLE, VoiceState.ERROR],
        VoiceState.PROCESSING: [VoiceState.SPEAKING, VoiceState.IDLE, VoiceState.INTERRUPTED, VoiceState.ERROR],
        VoiceState.SPEAKING: [VoiceState.IDLE, VoiceState.INTERRUPTED, VoiceState.LISTENING, VoiceState.ERROR],
        VoiceState.INTERRUPTED: [VoiceState.LISTENING, VoiceState.IDLE],
        VoiceState.ERROR: [VoiceState.IDLE, VoiceState.LISTENING]
    }

    def __init__(self, on_state_change: Optional[Callable[[VoiceState, VoiceState, int], None]] = None):
        self._current_state = VoiceState.IDLE
        self._current_generation_id = 0
        self.on_state_change = on_state_change

    @property
    def current_state(self) -> VoiceState:
        return self._current_state

    @property
    def current_generation_id(self) -> int:
        return self._current_generation_id

    def start_new_generation(self) -> int:
        self._current_generation_id += 1
        return self._current_generation_id

    def is_generation_valid(self, gen_id: int) -> bool:
        return gen_id == self._current_generation_id

    def transition_to(self, new_state: VoiceState, reason: str = "") -> bool:
        if new_state == self._current_state:
            return True

        allowed = self.ALLOWED_TRANSITIONS.get(self._current_state, [])
        if new_state not in allowed:
            logger.warning(f"[VoiceStateMachine] Transición no permitida: {self._current_state.value} -> {new_state.value} (Motivo: {reason})")
            return False

        old_state = self._current_state
        self._current_state = new_state
        logger.info(f"[VoiceStateMachine] {old_state.value} -> {new_state.value} (Gen: {self._current_generation_id}, Motivo: {reason})")

        if self.on_state_change:
            try:
                self.on_state_change(old_state, new_state, self._current_generation_id)
            except Exception as e:
                logger.error(f"[VoiceStateMachine] Error en callback: {e}")

        return True

    def trigger_barge_in(self) -> bool:
        """
        Invalida la generación actual e interrumpe el habla de inmediato.
        """
        # Incrementar generación para invalidar cualquier chunk tardío
        self._current_generation_id += 1
        logger.info(f"[VoiceStateMachine] ¡Barge-in! Nueva generación activa: {self._current_generation_id}")

        if self._current_state in [VoiceState.SPEAKING, VoiceState.PROCESSING]:
            self.transition_to(VoiceState.INTERRUPTED, reason="Barge-in de usuario")
            return self.transition_to(VoiceState.LISTENING, reason="Escuchando nueva consulta")
        elif self._current_state != VoiceState.LISTENING:
            return self.transition_to(VoiceState.LISTENING, reason="Forzado a escuchar")
        return True
