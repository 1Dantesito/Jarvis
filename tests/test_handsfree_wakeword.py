import time
from core.wakeword.detector import WakeWordDetector, ConversationState

def test_wakeword_detection():
    detector = WakeWordDetector(keyword="jarvis")
    assert detector.detect_wake_word("Jarvis pon música") is True
    assert detector.detect_wake_word("Oye Jarvis qué hora es") is True
    assert detector.detect_wake_word("Hey Jarvis cómo estás") is True
    assert detector.detect_wake_word("Hola Jarvis") is True
    assert detector.detect_wake_word("pásame la sal por favor") is False
    assert detector.detect_wake_word("la televisión está prendida") is False

def test_command_extraction():
    detector = WakeWordDetector(keyword="jarvis")
    
    has_wake, cmd = detector.extract_command("Jarvis, pon música de rock")
    assert has_wake is True
    assert cmd == "pon música de rock"

    has_wake, cmd = detector.extract_command("Oye Jarvis: ¿qué tengo pendiente?")
    assert has_wake is True
    assert cmd == "¿qué tengo pendiente?"

    has_wake, cmd = detector.extract_command("Jarvis")
    assert has_wake is True
    assert cmd == ""

    has_wake, cmd = detector.extract_command("conversación entre amigos")
    assert has_wake is False
    assert cmd == "conversación entre amigos"

def test_conversation_window_lifecycle():
    detector = WakeWordDetector(keyword="jarvis", window_seconds=2)
    assert detector.state == ConversationState.BACKGROUND

    # 1. Ruido en background -> descartado
    should_proc, cmd = detector.process_incoming_speech("hola qué tal cómo estás")
    assert should_proc is False
    assert detector.state == ConversationState.BACKGROUND

    # 2. Wake word -> activa ventana
    should_proc, cmd = detector.process_incoming_speech("Oye Jarvis pon la calculadora")
    assert should_proc is True
    assert cmd == "pon la calculadora"
    assert detector.state == ConversationState.ACTIVE

    # 3. Siguiente comando sin decir 'Jarvis' (dentro de la ventana de 2 segundos)
    should_proc, cmd = detector.process_incoming_speech("ahora abre el bloc de notas")
    assert should_proc is True
    assert cmd == "ahora abre el bloc de notas"
    assert detector.state == ConversationState.ACTIVE

    # 4. Esperar a que expire la ventana
    time.sleep(2.1)
    detector.check_window_expiration()
    assert detector.state == ConversationState.BACKGROUND

    # 5. Tras expirar, el ruido se descarta de nuevo
    should_proc, cmd = detector.process_incoming_speech("comentario cualquiera")
    assert should_proc is False

def test_background_listener_lifecycle():
    from core.wakeword.listener import BackgroundWakeWordListener

    received_commands = []
    def on_wake(cmd):
        received_commands.append(cmd)

    listener = BackgroundWakeWordListener(keyword="jarvis", on_wake_callback=on_wake)
    assert listener.is_running is False

    started = listener.start()
    assert started is True
    assert listener.is_running is True

    # 1. Frase sin wake word -> no se procesa
    listener.feed_transcript("ruido de fondo en la habitación")
    time.sleep(0.15)
    assert len(received_commands) == 0

    # 2. Frase con wake word -> callback disparado
    listener.feed_transcript("Oye Jarvis, qué hora es")
    time.sleep(0.2)
    assert len(received_commands) == 1
    assert received_commands[0] == "qué hora es"

    listener.stop()
    assert listener.is_running is False


def test_handsfree_frontend_conversational_window():
    import os
    js_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'script.js'))
    assert os.path.exists(js_path)
    with open(js_path, 'r', encoding='utf-8') as f:
        js = f.read()

    # 1. Ventana conversacional de seguimiento (8 segundos)
    assert "openConversationalWindow" in js
    assert "resetConversationTimer" in js
    assert "closeConversationalWindow" in js
    assert "isConversationActive" in js
    assert "CONVERSATION_WINDOW_MS = 8000" in js

    # 2. Respuestas vocales naturales ante el wake word solitario
    assert "playSpokenAck" in js
    assert "¿Dígame, señor?" in js
    assert "¿Sí? Te escucho." in js

    # 3. Barge-in activo que interrumpe el audio actual y emite websocket barge_in
    assert 'type: "barge_in"' in js
    assert 'uiState.voiceState = "INTERRUPTED"' in js
    assert "clearTTSAudioQueue" in js

    # 4. Debounce rápido de 850ms para transcripciones intermedias
    assert "speechSilenceTimer" in js
    assert "850" in js

