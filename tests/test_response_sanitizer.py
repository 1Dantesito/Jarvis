import pytest
from core.response_sanitizer import ResponseSanitizer

def test_placeholder_removal():
    raw = "Hola {usuario}, tu {nombre} es válido."
    cleaned = ResponseSanitizer.sanitize(raw)
    assert "{usuario}" not in cleaned
    assert "{nombre}" not in cleaned
    assert "Hola" in cleaned

def test_technical_tokens_cleanup():
    raw = "El resultado es None y la llamada call_open_app retornó null."
    cleaned = ResponseSanitizer.sanitize(raw)
    assert "None" not in cleaned
    assert "null" not in cleaned
    assert "call_open_app" not in cleaned

def test_markdown_and_links_cleanup():
    raw = "Revisa este [sitio web](https://google.com) y **este texto** en _cursiva_."
    cleaned = ResponseSanitizer.sanitize_for_speech(raw)
    assert "https://google.com" not in cleaned
    assert "sitio web" in cleaned
    assert "**" not in cleaned
    assert "este texto" in cleaned

def test_name_repetition_suppression():
    raw = "Hola Dante. Dante, ¿en qué te puedo colaborar Dante?"
    cleaned = ResponseSanitizer.sanitize(raw, user_name="Dante")
    # El nombre solo debe aparecer una vez
    assert cleaned.count("Dante") == 1

def test_speech_friendly_expansion():
    raw = "El Dr. Pérez tiene una app para la PC con 50% de descuento y $10 vs €10."
    speech = ResponseSanitizer.sanitize_for_speech(raw)
    assert "Doctor" in speech
    assert "aplicación" in speech
    assert "computadora" in speech
    assert "por ciento" in speech
    assert "dólares" in speech
    assert "versus" in speech

def test_beautiful_markdown_numbered_list():
    raw = "Aquí tienes cosas cotidianas: 1. **Café**: Se enfría rápido. 2. **Llaves**: Se pierden siempre. ¿Cuál buscas?"
    cleaned = ResponseSanitizer.sanitize(raw)
    assert "cotidianas:\n\n1. **Café**" in cleaned
    assert "rápido.\n\n2. **Llaves**" in cleaned
    assert "siempre.\n\n¿Cuál buscas?" in cleaned

def test_beautiful_markdown_bullet_list():
    raw = "Recomendaciones: - Primer consejo - Segundo consejo"
    cleaned = ResponseSanitizer.sanitize(raw)
    assert "Recomendaciones:\n\n- Primer consejo" in cleaned
    assert "consejo\n\n- Segundo consejo" in cleaned

def test_beautiful_markdown_unicode_bullets():
    raw = "Tareas:\n• Comprar leche\n· Pagar internet"
    cleaned = ResponseSanitizer.sanitize(raw)
    assert "- Comprar leche" in cleaned
    assert "- Pagar internet" in cleaned

