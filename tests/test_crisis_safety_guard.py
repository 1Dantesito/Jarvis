"""
Suite de pruebas exhaustivas para CrisisSafetyGuard (Fase D: Cerebro Relacional).
Valida:
  1. Capa 1 Fast-Path Determinista (0 ms, 0 llamadas a LLM ante riesgo explícito).
  2. Capa 2 Clasificador LLM Aislado (llamada solo ante afecto negativo).
  3. Gating selectivo: Omitir Capa 2 en mensajes neutros y técnicos (0 ms, 0 cuota consumida).
  4. Failsafe estricto: Timeout en Capa 2 cae a MILD, NUNCA a NORMAL.
  5. Failsafe estricto: Error de red/proveedor en Capa 2 cae a MILD, NUNCA a NORMAL.
  6. Respuestas canónicas y sesgo conservador ante AMBIGUO -> MILD y SI -> CRISIS.
  7. Directorio de helplines en memoria RAM vía LocationProvider y fallback universal.
  8. Protocolo multiturno sostenido (anti-enmascaramiento: no salir con un solo 'estoy bien').
  9. Re-escalamiento inmediato si la aflicción reaparece durante la desescalada.
  10. Integración con JarvisOrchestrator (bloqueo preventivo de herramientas y respuesta directa).
"""

import pytest
import asyncio
from core.crisis_guard import (
    CrisisSafetyGuard,
    CrisisRiskLevel,
    CrisisState,
    CrisisDecision,
    get_crisis_helpline,
    normalize_crisis_text,
    CRISIS_HELPLINES,
    UNIVERSAL_HELPLINE
)
from core.location_provider import LocationProvider
from providers.mock_provider import MockAIProvider
from core.orchestrator import JarvisOrchestrator

@pytest.fixture(autouse=True)
def reset_location_cache():
    old_cache = LocationProvider._cache
    old_time = LocationProvider._cache_time
    yield
    LocationProvider._cache = old_cache
    LocationProvider._cache_time = old_time

@pytest.mark.asyncio
async def test_layer_1_fast_path_zero_latency():
    """Verifica que la Capa 1 intercepte métodos directos y despedidas en 0 ms sin invocar al LLM."""
    guard = CrisisSafetyGuard()
    mock_p = MockAIProvider()

    direct_cases = [
        "me quiero suicidar",
        "voy a acabar con mi vida",
        "quiero matarme ya no aguanto",
        "me voy a quitar la vida",
        "tomar veneno y terminar con todo",
        "voy a saltar del puente",
        "cortarme las venas",
        "sobredosis de pastillas",
        "esta es mi despedida adios a todos para siempre"
    ]

    for phrase in direct_cases:
        guard.reset_state()
        mock_p.calls_count = 0
        decision = await guard.evaluate_message(phrase, mock_p)

        assert decision.risk_level == CrisisRiskLevel.CRISIS, f"Falló para: {phrase}"
        assert decision.score == 1.0
        assert decision.layer_triggered == "LAYER_1_REGEX"
        assert decision.is_interruptive is True
        assert decision.response_text is not None
        assert "línea de apoyo" in decision.response_text or "linea de apoyo" in decision.response_text
        # Asertar que NUNCA llamó al LLM (ahorro de latencia y cuota)
        assert mock_p.calls_count == 0, f"Capa 1 no debió invocar LLM para: {phrase}"

@pytest.mark.asyncio
async def test_layer_2_called_only_on_negative_affect():
    """Verifica que la Capa 2 solo se invoque cuando Capa 1 no disparó Y existe afecto negativo."""
    guard = CrisisSafetyGuard()
    mock_p = MockAIProvider()

    # Frase con carga afectiva negativa / desesperanza sutil pero sin método explícito de Capa 1
    text = "me siento profundamente solo, triste y siento que nada tiene sentido"
    mock_p.forced_response = "AMBIGUO"
    mock_p.calls_count = 0

    decision = await guard.evaluate_message(text, mock_p)

    assert mock_p.calls_count == 1, "Capa 2 debió ser invocada para evaluar afecto negativo"
    assert decision.risk_level == CrisisRiskLevel.MILD
    assert decision.layer_triggered == "LAYER_2_LLM"
    assert mock_p.last_model == guard.fast_model

@pytest.mark.asyncio
async def test_layer_2_skipped_on_neutral_and_technical_messages():
    """Verifica que mensajes neutros y técnicos omitan completamente la Capa 2 (0 llamadas a LLM)."""
    guard = CrisisSafetyGuard()
    mock_p = MockAIProvider()

    neutral_messages = [
        "qué es un socket TCP en redes",
        "dime la hora actual",
        "abre la calculadora de windows",
        "crea un archivo de texto con el resumen de la reunión",
        "cuál es la capital de Australia",
        "pon algo de música clásica para programar",
        "busca en google documentación de python 3.12",
        "solo necesito ver mis pendientes",
        "solo abre youtube",
        "para que sirve este comando",
        "adios, nos vemos manana",
        "gracias por todo tu apoyo en el codigo"
    ]

    for msg in neutral_messages:
        mock_p.calls_count = 0
        decision = await guard.evaluate_message(msg, mock_p)

        assert decision.risk_level == CrisisRiskLevel.NORMAL
        assert decision.score == 0.0
        assert decision.layer_triggered == "NONE"
        assert decision.is_interruptive is False
        assert mock_p.calls_count == 0, f"Mensaje neutro '{msg}' gastó llamada a Capa 2"

@pytest.mark.asyncio
async def test_layer_2_timeout_falls_back_to_mild_never_normal():
    """
    ASERCIÓN CRÍTICA DE SEGURIDAD:
    Si la Capa 2 sufre un timeout ante un mensaje con afecto negativo,
    el guardián DEBE degradar a MILD (contención suave preventiva) y NUNCA a NORMAL.
    """
    # Configuramos timeout ultra corto de prueba
    guard = CrisisSafetyGuard(timeout_seconds=0.1)
    mock_p = MockAIProvider()
    mock_p.forced_delay = 0.4  # Mayor que el timeout para forzar TimeoutError

    distress_text = "estoy desesperado y todo esto se convirtió en una pesadilla agotadora"
    decision = await guard.evaluate_message(distress_text, mock_p)

    # Verificación de degradación conservadora
    assert decision.risk_level == CrisisRiskLevel.MILD, "Bajo timeout ante aflicción, el riesgo DEBE ser MILD"
    assert decision.risk_level != CrisisRiskLevel.NORMAL, "NUNCA debe clasificar como NORMAL ante timeout"
    assert decision.score == 0.50
    assert decision.layer_triggered == "FAILSAFE_FALLBACK"
    assert decision.is_interruptive is True
    assert decision.response_text is not None

@pytest.mark.asyncio
async def test_layer_2_error_falls_back_to_mild_never_normal():
    """
    ASERCIÓN CRÍTICA DE SEGURIDAD:
    Si la Capa 2 sufre un error de red o de API ante un mensaje con afecto negativo,
    el guardián DEBE degradar a MILD y NUNCA a NORMAL.
    """
    guard = CrisisSafetyGuard()
    mock_p = MockAIProvider()
    mock_p.forced_error = "503 Service Unavailable / Connection timeout to inference backend"

    distress_text = "siento una angustia que me apaga y me duele existir"
    decision = await guard.evaluate_message(distress_text, mock_p)

    assert decision.risk_level == CrisisRiskLevel.MILD
    assert decision.risk_level != CrisisRiskLevel.NORMAL
    assert decision.layer_triggered == "FAILSAFE_FALLBACK"
    assert decision.score == 0.50
    assert decision.is_interruptive is True

@pytest.mark.asyncio
async def test_layer_2_conservative_bias_si_ambiguo_no():
    """Verifica el comportamiento estricto de las 3 salidas del clasificador LLM."""
    guard = CrisisSafetyGuard()
    mock_p = MockAIProvider()

    # 1. SI -> CRISIS
    mock_p.forced_response = "SI"
    dec_si = await guard.evaluate_message("ya me cansé de todo, gracias por acompañarme hasta hoy", mock_p)
    assert dec_si.risk_level == CrisisRiskLevel.CRISIS
    assert dec_si.score >= 0.80
    assert dec_si.layer_triggered == "LAYER_2_LLM"
    assert dec_si.is_interruptive is True

    # 2. AMBIGUO -> MILD
    guard.reset_state()
    mock_p.forced_response = "AMBIGUO"
    dec_amb = await guard.evaluate_message("estoy triste y no sé qué hacer con mi vida", mock_p)
    assert dec_amb.risk_level == CrisisRiskLevel.MILD
    assert dec_amb.score == 0.55
    assert dec_amb.layer_triggered == "LAYER_2_LLM"
    assert dec_amb.is_interruptive is True

    # 3. NO -> NORMAL
    guard.reset_state()
    mock_p.forced_response = "NO"
    dec_no = await guard.evaluate_message("estoy cansado del trabajo pero mañana entrego el informe", mock_p)
    assert dec_no.risk_level == CrisisRiskLevel.NORMAL
    assert dec_no.layer_triggered == "LAYER_2_LLM"
    assert dec_no.is_interruptive is False

def test_location_aware_helplines_and_universal_fallback():
    """Verifica la resolución en memoria RAM (<0.1 ms) del directorio de helplines."""
    # Colombia
    LocationProvider._cache = {"country_code": "CO"}
    assert "106 / 192" in get_crisis_helpline()

    # España
    LocationProvider._cache = {"country_code": "ES"}
    assert "024" in get_crisis_helpline()

    # Estados Unidos
    LocationProvider._cache = {"country_code": "US"}
    assert "988" in get_crisis_helpline()

    # México
    LocationProvider._cache = {"country_code": "MX"}
    assert "800 911 2000" in get_crisis_helpline()

    # Fallback Universal cuando no hay país o es desconocido
    LocationProvider._cache = {"country_code": "ZZ"}
    fallback_text = get_crisis_helpline()
    assert "123 o 911" in fallback_text
    assert fallback_text == UNIVERSAL_HELPLINE

    LocationProvider._cache = None
    assert get_crisis_helpline() == UNIVERSAL_HELPLINE

@pytest.mark.asyncio
async def test_multi_turn_anti_masking_protocol():
    """
    Verifica que el protocolo de crisis requiera estabilidad dialogada sostenida
    y NO se desactive con un simple 'ya estoy bien'.
    """
    guard = CrisisSafetyGuard()
    mock_p = MockAIProvider()

    # Turno 1: Activación de crisis
    d1 = await guard.evaluate_message("me quiero suicidar", mock_p)
    assert d1.risk_level == CrisisRiskLevel.CRISIS
    assert guard.current_state == CrisisState.ACTIVE_CRISIS

    # Turno 2: Usuario intenta salir con frase rápida de calma -> Anti-enmascaramiento retiene
    d2 = await guard.evaluate_message("ya estoy bien, tranquilo", mock_p)
    assert d2.risk_level == CrisisRiskLevel.MILD
    assert d2.layer_triggered == "MULTI_TURN_TRACKER"
    assert guard.current_state == CrisisState.POST_CRISIS_TURN_1
    assert "¿Hay alguien contigo" in d2.response_text or "alguien de confianza" in d2.response_text

    # Turno 3: Usuario confirma compañía real
    d3 = await guard.evaluate_message("sí, estoy con mi hermano y ya hablé con él", mock_p)
    assert d3.risk_level == CrisisRiskLevel.MILD
    assert guard.current_state == CrisisState.POST_CRISIS_TURN_2
    assert "Aquí sigo contigo" in d3.response_text

    # Turno 4: Confirmación reflexiva -> Pasa a cool-down de 3 turnos
    d4 = await guard.evaluate_message("gracias Jarvis, estoy mucho más calmado", mock_p)
    assert d4.risk_level == CrisisRiskLevel.NORMAL
    assert guard.current_state == CrisisState.MONITORING_COOLDOWN
    assert d4.cooldown_turns_remaining == 3

    # Turnos 5, 6, 7: Monitoreo decreciente
    await guard.evaluate_message("qué hora es", mock_p)
    assert guard.current_state == CrisisState.MONITORING_COOLDOWN
    await guard.evaluate_message("cuál es el clima", mock_p)
    assert guard.current_state == CrisisState.MONITORING_COOLDOWN
    await guard.evaluate_message("abre notas", mock_p)
    # Al consumir los 3 turnos, regresa a inactivo
    assert guard.current_state == CrisisState.INACTIVE

@pytest.mark.asyncio
async def test_multi_turn_re_escalation_if_distress_reappears():
    """Verifica que si la aflicción reaparece en plena desescalada, el protocolo regrese a CRISIS."""
    guard = CrisisSafetyGuard()
    mock_p = MockAIProvider()

    # Turno 1: Crisis
    await guard.evaluate_message("me quiero morir", mock_p)
    assert guard.current_state == CrisisState.ACTIVE_CRISIS

    # Turno 2: Calma aparente
    await guard.evaluate_message("ya pasó, era broma", mock_p)
    assert guard.current_state == CrisisState.POST_CRISIS_TURN_1

    # Turno 3: Recaída / aflicción extrema
    d3 = await guard.evaluate_message("mentira, no puedo más, voy a tomar veneno", mock_p)
    assert d3.risk_level == CrisisRiskLevel.CRISIS
    assert guard.current_state == CrisisState.ACTIVE_CRISIS
    assert d3.layer_triggered == "LAYER_1_REGEX"

@pytest.mark.asyncio
async def test_orchestrator_integration_with_crisis_guard():
    """Verifica que el orquestador intercepte preventivamente y no ejecute herramientas."""
    mock_p = MockAIProvider()
    orch = JarvisOrchestrator(primary_provider=mock_p)

    res = await orch.process_user_input("me quiero suicidar")
    assert res["success"] is True
    assert res["action_type"] == "crisis_guard_interrupt"
    assert "CRISIS" in res["action_detail"]
    assert res["tools_executed"] == []
    assert "línea de apoyo" in res["response_text"] or "linea de apoyo" in res["response_text"]

    # Verificación en streaming
    stream_events = []
    async for event in orch.process_user_input_stream("me quiero suicidar"):
        stream_events.append(event)

    types = [e.get("type") for e in stream_events]
    assert "sentence" in types
    assert "response_end" in types
    end_event = next(e for e in stream_events if e.get("type") == "response_end")
    assert end_event.get("action_type") == "crisis_guard_interrupt"
    assert end_event.get("tools_executed") == []

@pytest.mark.asyncio
async def test_orchestrator_e2e_crisis_blocks_tools_and_uses_country_helpline():
    """
    Test End-to-End en el Orquestador:
    Simula un mensaje real donde el usuario pide ejecutar una herramienta pero expresa riesgo CRISIS.
    Verifica que las herramientas NO se ejecuten y se inyecte la línea de ayuda del país en caché (CO).
    """
    LocationProvider._cache = {"country_code": "CO"}
    mock_p = MockAIProvider()
    orch = JarvisOrchestrator(primary_provider=mock_p)

    # Prompt que combina una acción de escritorio con ideación suicida
    prompt = "abre la calculadora y me voy a suicidar"
    res = await orch.process_user_input(prompt)

    assert res["success"] is True
    assert res["tools_executed"] == [], "Las herramientas DEBEN estar completamente bloqueadas ante CRISIS"
    assert res["action_type"] == "crisis_guard_interrupt"
    assert "(CRISIS)" in res["action_detail"]
    assert "106 / 192" in res["response_text"], "Debe incluir la línea de Colombia desde la memoria RAM"

@pytest.mark.asyncio
async def test_orchestrator_e2e_mild_blocks_tools_and_emits_containment():
    """
    Test End-to-End en el Orquestador:
    Simula un mensaje donde el usuario pide una herramienta pero expresa dolor/ambigüedad (MILD).
    Verifica que las herramientas se bloqueen y se emita la respuesta de contención suave.
    """
    LocationProvider._cache = {"country_code": "ES"}
    mock_p = MockAIProvider()
    mock_p.forced_response = "AMBIGUO"
    orch = JarvisOrchestrator(primary_provider=mock_p)

    prompt = "abre el bloc de notas, me invade una tristeza insoportable y un vacio total"
    res = await orch.process_user_input(prompt)

    assert res["success"] is True
    assert res["tools_executed"] == [], "Las herramientas DEBEN estar bloqueadas en contención MILD"
    assert res["action_type"] == "crisis_guard_interrupt"
    assert "(MILD)" in res["action_detail"]
    assert "Te escucho y percibo que estás pasando por un momento muy pesado" in res["response_text"]

@pytest.mark.asyncio
async def test_circuit_breaker_trips_after_consecutive_failures():
    """
    Verifica que el Circuit Breaker de Capa 2 se abra tras fallos repetidos
    y fast-failee a MILD en 0 ms sin seguir llamando al proveedor de IA.
    """
    guard = CrisisSafetyGuard(circuit_failure_threshold=3, circuit_cooldown_seconds=10.0)
    mock_p = MockAIProvider()
    mock_p.forced_error = "500 Internal Server Error (API Down)"

    distress_msg = "estoy triste y desesperado sin ganas de seguir"

    # 3 fallos consecutivos
    for i in range(3):
        dec = await guard.evaluate_message(distress_msg, mock_p)
        assert dec.risk_level == CrisisRiskLevel.MILD
        assert guard.circuit_consecutive_failures == i + 1

    assert guard.is_circuit_open() is True, "El circuit breaker debe estar ABIERTO tras 3 fallos"

    # 4ta llamada: debe entrar en Fast-Fail (0 ms, sin llamar a la API)
    calls_before = mock_p.calls_count
    dec_fast_fail = await guard.evaluate_message(distress_msg, mock_p)

    assert mock_p.calls_count == calls_before, "No debe invocar al proveedor cuando el circuito está abierto"
    assert dec_fast_fail.risk_level == CrisisRiskLevel.MILD
    assert dec_fast_fail.layer_triggered == "FAILSAFE_FALLBACK"
    assert "Circuit breaker ABIERTO" in dec_fast_fail.reason

    # Reset
    guard.reset_state()
    assert guard.is_circuit_open() is False
    assert guard.circuit_consecutive_failures == 0

@pytest.mark.asyncio
async def test_circuit_breaker_recovery_half_open_to_closed():
    """
    Verifica el ciclo de vida de recuperación del Circuit Breaker:
    ABIERTO -> expira cooldown (HALF-OPEN) -> llamada exitosa -> CERRADO (recuperación total).
    """
    import time
    guard = CrisisSafetyGuard(circuit_failure_threshold=3, circuit_cooldown_seconds=5.0)
    mock_p = MockAIProvider()
    mock_p.forced_error = "503 Backend Overloaded"

    distress_msg = "siento una angustia que me apaga y me duele existir"

    # 1. Provocar apertura del circuito tras 3 fallos
    for _ in range(3):
        await guard.evaluate_message(distress_msg, mock_p)

    assert guard.is_circuit_open() is True
    assert guard.circuit_consecutive_failures == 3

    # 2. Simular expiración del cooldown temporal (transición a HALF-OPEN)
    guard._circuit_open_until = time.time() - 0.1
    assert guard.is_circuit_open() is False, "Al expirar el cooldown debe permitir la llamada de prueba (HALF-OPEN)"
    assert guard._circuit_open_until == 0.0

    # 3. El proveedor se ha recuperado y responde con éxito
    mock_p.forced_error = None
    mock_p.forced_response = "AMBIGUO"

    dec_recovered = await guard.evaluate_message(distress_msg, mock_p)
    assert dec_recovered.risk_level == CrisisRiskLevel.MILD
    assert dec_recovered.layer_triggered == "LAYER_2_LLM"

    # 4. Verificar que el circuito quedó completamente CERRADO y con fallos en 0
    assert guard.circuit_consecutive_failures == 0
    assert guard.is_circuit_open() is False
