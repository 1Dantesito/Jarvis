import pytest
from core.voice_state_machine import VoiceStateMachine, VoiceState

def test_generation_id_increment_on_bargein():
    sm = VoiceStateMachine()
    gen1 = sm.start_new_generation()
    assert gen1 == 1
    assert sm.is_generation_valid(1) is True

    # Transición a hablando
    sm.transition_to(VoiceState.PROCESSING)
    sm.transition_to(VoiceState.SPEAKING)
    assert sm.current_state == VoiceState.SPEAKING

    # Usuario interrumpe
    sm.trigger_barge_in()
    assert sm.current_state == VoiceState.LISTENING
    assert sm.current_generation_id == 2

    # Chunk tardío de generación 1 debe ser inválido
    assert sm.is_generation_valid(1) is False
    assert sm.is_generation_valid(2) is True
