import pytest
from core.sentence_buffer import SentenceBuffer
from core.voice_state_machine import VoiceStateMachine, VoiceState
from core.voice_pipeline import VoiceMetrics

def test_sentence_buffer_splitting():
    buf = SentenceBuffer(min_chunk_length=10)
    
    # Agregar tokens con delimitadores fuertes
    chunks = buf.add_token("Claro. ")
    assert len(chunks) == 1
    assert chunks[0] == "Claro."

    chunks2 = buf.add_token("Puedo abrir la calculadora por ti. ")
    assert len(chunks2) == 1
    assert chunks2[0] == "Puedo abrir la calculadora por ti."

    # Vaciar remanente
    buf.add_token("Dame un segundo")
    flushed = buf.flush()
    assert len(flushed) == 1
    assert flushed[0] == "Dame un segundo"

def test_sentence_buffer_markdown_cleaning():
    raw = "**Hola Dante**, ¿en qué *puedo* ayudarte hoy?"
    clean = SentenceBuffer.clean_for_speech(raw)
    assert clean == "Hola Dante, ¿en qué puedo ayudarte hoy?"
    assert "*" not in clean

def test_voice_state_machine_transitions():
    sm = VoiceStateMachine()
    assert sm.current_state == VoiceState.IDLE

    # Transición válida: IDLE -> LISTENING
    assert sm.transition_to(VoiceState.LISTENING) is True
    assert sm.current_state == VoiceState.LISTENING

    # Transición válida: LISTENING -> PROCESSING
    assert sm.transition_to(VoiceState.PROCESSING) is True
    assert sm.current_state == VoiceState.PROCESSING

    # Transición válida: PROCESSING -> SPEAKING
    assert sm.transition_to(VoiceState.SPEAKING) is True
    assert sm.current_state == VoiceState.SPEAKING

    # Transición inválida: SPEAKING -> LISTENING directo sin barge-in/idle
    # Barge-in directo:
    assert sm.trigger_barge_in() is True
    assert sm.current_state == VoiceState.LISTENING

def test_voice_metrics_calculation():
    metrics = VoiceMetrics()
    metrics.mark_audio_end()
    metrics.mark_stt_final()
    metrics.mark_llm_first_token()
    metrics.mark_first_sentence()
    metrics.mark_first_audio_played()
    metrics.mark_response_end()

    report = metrics.calculate_report()
    assert "time_to_first_audio_ms" in report
    assert "total_roundtrip_ms" in report

def test_sentence_tts_pipeline_stream():
    from core.voice_pipeline import SentenceTTSPipeline, SentenceBuffer
    pipeline = SentenceTTSPipeline(min_length=15, user_name="Dante")
    
    # Simular streaming de tokens desde el LLM
    tokens = ["Hola ", "Dante. ", "Estoy ", "listo ", "para ", "ayudarte ", "hoy. "]
    all_packets = []
    for t in tokens:
        packets = pipeline.feed_token(t)
        all_packets.extend(packets)

    assert len(all_packets) >= 1
    # Cada paquete debe contener texto sanitizado y audio_url generado
    first = all_packets[0]
    assert "Hola Dante." in first["text"] or "Dante" in first["text"]
    assert "audio_url" in first
    assert "/api/tts/stream?text=" in first["audio_url"]
    assert first["is_final"] is False

    # Vaciar buffer remanente
    final_packets = pipeline.finish()
    for p in final_packets:
        assert p["is_final"] is True
        assert "/api/tts/stream?text=" in p["audio_url"]

