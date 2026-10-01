"""
CrisisSafetyGuard — Guardián de Seguridad de Dos Capas para JARVIS (Roadmap Fase D).
Proporciona mitigación algorítmica de daños ante ideación autolítica y aflicción extrema:
  - Capa 1: Fast-Path determinista por regex normalizado (0 ms, casos inequívocos de máxima confianza).
  - Capa 2: Clasificador de seguridad clínica aislado vía LLM ligero (timeout estricto <= 2.0s, modelo fast/lite).
  - Regla de sesgo conservador: Timeout/Error/Ambigüedad -> MILD (Contención Suave), NUNCA NORMAL.
  - Filtro selectivo de carga afectiva: Mensajes neutros/técnicos evitan la invocación a la Capa 2 (0 ms, 0 tokens).
  - Directorio dinámico de líneas de crisis vía LocationProvider (exclusivamente RAM, 0 ms).
  - Protocolo de salida multiturno sostenido (anti-enmascaramiento).

AVISO CLÍNICO OBLIGATORIO:
CrisisSafetyGuard es un módulo heurístico y algorítmico de mitigación de daños, NO un dispositivo
médico ni un clasificador psicométrico clínicamente validado. No sustituye la intervención psiquiátrica
ni el criterio humano calificado. Su propósito exclusivo es la contención primaria inmediata y la
derivación urgente a líneas profesionales acreditadas.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import unicodedata
import re
import asyncio
import time
from core.logger import logger
from core.config import settings
from core.location_provider import LocationProvider
from core.ai_provider import AIProvider

class CrisisRiskLevel(str, Enum):
    CRISIS = "CRISIS"
    MILD = "MILD"
    NORMAL = "NORMAL"

class CrisisState(str, Enum):
    INACTIVE = "INACTIVE"
    ACTIVE_CRISIS = "ACTIVE_CRISIS"
    POST_CRISIS_TURN_1 = "POST_CRISIS_TURN_1"
    POST_CRISIS_TURN_2 = "POST_CRISIS_TURN_2"
    MONITORING_COOLDOWN = "MONITORING_COOLDOWN"

@dataclass
class CrisisDecision:
    risk_level: CrisisRiskLevel
    score: float
    reason: str
    layer_triggered: str  # "LAYER_1_REGEX", "LAYER_2_LLM", "FAILSAFE_FALLBACK", "MULTI_TURN_TRACKER", "NONE"
    helpline_text: Optional[str] = None
    response_text: Optional[str] = None
    is_interruptive: bool = False
    state: CrisisState = CrisisState.INACTIVE
    cooldown_turns_remaining: int = 0

CRISIS_HELPLINES: Dict[str, str] = {
    "CO": "Línea 106 / 192 (Salud Mental Colombia)",
    "MX": "Línea de la Vida: 800 911 2000 (México)",
    "ES": "Línea 024 / Teléfono de la Esperanza: 717 033 717 (España)",
    "US": "988 Suicide & Crisis Lifeline (EE. UU.)",
    "AR": "Centro de Asistencia al Suicida: 135 (Argentina)",
    "CL": "*4141 'No Estás Solo' (Chile)"
}

UNIVERSAL_HELPLINE: str = (
    "Por favor, comunícate de inmediato con el número de emergencias de tu localidad "
    "(como el 123 o 911), acude al centro de salud más cercano o habla con alguien de tu entera "
    "confianza ahora mismo."
)

CRISIS_EVALUATION_SYSTEM_PROMPT = (
    "Actúa como un evaluador de seguridad clínica estricto. "
    "Tu única tarea es analizar si el mensaje del usuario contiene indicios "
    "directos, indirectos, velados o metafóricos de ideación suicida, autolesión, "
    "desesperanza terminal o despedida irreversible.\n"
    "Responde ÚNICAMENTE con una sola palabra en mayúsculas: SI, NO o AMBIGUO.\n"
    "No agregues explicaciones, puntuación ni texto adicional."
)

def get_crisis_helpline() -> str:
    """
    Obtiene la línea de ayuda correspondiente al país del usuario usando
    exclusivamente la memoria RAM de LocationProvider (0 ms, sin I/O de red).
    Si no hay caché o el país no está listado, retorna la recomendación universal.
    """
    try:
        country_code = LocationProvider.get_cached_country_code()
        if country_code and isinstance(country_code, str):
            code_upper = country_code.upper().strip()
            if code_upper in CRISIS_HELPLINES:
                return CRISIS_HELPLINES[code_upper]
    except Exception as e:
        logger.debug(f"[CrisisGuard] Error obteniendo helpline en caché: {e}")
    return UNIVERSAL_HELPLINE

def normalize_crisis_text(text: str) -> str:
    """
    Normalización Unicode NFD, remoción de acentos/diacríticos, minúsculas,
    colapso de repeticiones de caracteres y eliminación de puntuación.
    """
    if not text:
        return ""
    nfd = unicodedata.normalize("NFD", text)
    stripped = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    lowered = stripped.lower()
    # Colapsar repeticiones excesivas (ej: "adiiiioooos" -> "adios", "muuueeero" -> "muero")
    collapsed = re.sub(r'(.)\1{2,}', r'\1', lowered)
    cleaned = re.sub(r'[^a-z0-9\s]', ' ', collapsed)
    return " ".join(cleaned.split())


def is_media_entertainment_query(norm_text: str) -> bool:
    """
    Detecta si el mensaje es una búsqueda o reproducción de música, canciones o entretenimiento
    donde palabras como 'triste' califican a la obra artística o canción y no expresan crisis autolítica del usuario.
    """
    media_patterns = [
        r"\b(cancion|canciones|musica|track|tracks|rolas?|tema|temas|balada|baladas|melodia|melodias|playlist|album)\b.*\b(trist[a-z]*|melancol[a-z]*|desamor|llanto|llorar|dolor)\b",
        r"\b(trist[a-z]*|melancol[a-z]*|desamor)\b.*\b(cancion|canciones|musica|track|tracks|rolas?|tema|temas|balada|baladas|melodia|melodias|playlist|album)\b",
        r"\b(pon|reproduce|reproducir|play|toca|escucha|escuchar|oir|busca|buscar)\b.*\b(trist[a-z]*|melancol[a-z]*|desamor)\b",
        r"\b(pelicula|peliculas|video|videos|libro|libros|poema|poemas|serie|series|anime)\b.*\b(trist[a-z]*|melancol[a-z]*)\b"
    ]
    return any(re.search(pat, norm_text) for pat in media_patterns)


class CrisisSafetyGuard:
    """
    Guardián de Seguridad Relacional y Mitigación de Daños en Dos Capas.
    """

    # --- Capa 1: Expresiones Regulares de Alta Confianza (Fast-Path) ---
    _LAYER_1_PATTERNS = [
        # Ideación suicida directa e inequívoca (cualquier flexión o orden pronominal)
        re.compile(r"\b(suicid[a-z]+)\b"),
        re.compile(r"\b((me )?(quiero|voy a|pienso|planeo) matar(me)?)\b"),
        re.compile(r"\b(voy a acabar con mi vida|quiero acabar con mi vida|acabar con mi propia vida)\b"),
        re.compile(r"\b(no quiero vivir mas|ya no quiero vivir|no vale la pena vivir|para que vivir)\b"),
        re.compile(r"\b((me )?(voy a|quiero) quitar(me)? la vida)\b"),
        # Métodos letales explícitos
        re.compile(r"\b(tomar veneno|tomare veneno|beber veneno|ingerir veneno)\b"),
        re.compile(r"\b(tirarme del puente|saltar del puente|saltar al vacio|tirarme al tren|tirarme a las vias)\b"),
        re.compile(r"\b(cortarme las venas|cortar mis venas)\b"),
        re.compile(r"\b(sobredosis de pastillas|tomarme todas las pastillas|tomarme una caja de pastillas)\b"),
        re.compile(r"\b(ahorcarme|colgarme de una soga|ahorcar)\b"),
        re.compile(r"\b(dispararme en la cabeza|pegarme un tiro)\b"),
        # Despedidas explícitas irreversibles
        re.compile(r"\b(esta es mi despedida|esta es mi carta de despedida|les dejo esta carta)\b"),
        re.compile(r"\b(no estare aqui manana adios|ya no estare manana adios|adios a todos para siempre)\b")
    ]

    # --- Filtro Selectivo de Carga Emocional Negativa (Gating Permisivo para Capa 2) ---
    _NEGATIVE_AFFECT_PATTERNS = [
        re.compile(r"\b(suicid[a-z]+|autolesion[a-z]*|cortarm[ea]|matarm[ea]|acabar con mi vida)\b"),
        re.compile(r"\b(trist[a-z]*)\b"),
        re.compile(r"\b(me siento (profundamente |muy |tan )?sol[oa]|estoy (muy |tan |profundamente )?sol[oa]|mucha soledad|en soledad|soledad|sintiendome sol[oa]|completamente sol[oa]|vacio y sol[oa])\b"),
        re.compile(r"\b(cans[a-z]+|agot[a-z]+|fatig[a-z]+)\b"),
        re.compile(r"\b(desespera[a-z]+|desesperanza|desespero)\b"),
        re.compile(r"\b(dolor[a-z]*|sufro|sufriendo|sufrimiento|sufre)\b"),
        re.compile(r"\b(llor[a-z]+|llanto|lagrima[s]?)\b"),
        re.compile(r"\b(no sirvo|soy una carga|inutil|estorbo)\b"),
        re.compile(r"\b(pesadilla|oscuridad|vaci[oa][a-z]*)\b"),
        re.compile(r"\b(sin sentido seguir|mi vida no tiene sentido|nada tiene sentido|de que sirve vivir|para que vivir|para que seguir( viviendo)?|no vale de nada vivir|no tiene caso seguir|no tiene caso vivir)\b"),
        re.compile(r"\b(me rindo|rendir[a-z]*|rendid[oa]|rindo)\b"),
        re.compile(r"\b(hart[a-z]+)\b"),
        re.compile(r"\b(angustia[a-z]*|ansiedad|panico|miedo|temor)\b"),
        re.compile(r"\b(quiero morir|deseo morir|preferiria morir|preferiria estar muert[oa]|ganas de morir|ojala estuviera muert[oa]|morirme)\b"),
        re.compile(r"\b(carta de despedida|despedida final|adios para siempre|adios a todos para siempre|hasta aqui llegue mi vida|me voy para siempre de este mundo)\b"),
        re.compile(r"\b(culpa[a-z]*|culpable)\b"),
        re.compile(r"\b(no aguanto|no puedo mas|ya no puedo|no doy mas|sin fuerzas|no tengo fuerzas)\b"),
        re.compile(r"\b(para que seguir|no hay salida|sin esperanza|sin ganas|no tengo ganas|perdi la esperanza)\b"),
        re.compile(r"\b(nadie me (quiere|importa)|a nadie le importo|a quien le importa)\b"),
        re.compile(r"\b(odio mi vida|asqueado de vivir|apagarme|me apague|apagad[oa]|hundid[oa]|destrozad[oa]|roto por dentro)\b"),
        re.compile(r"\b(desaparecer|borrarme|no despertar|dormirme para siempre)\b"),
        re.compile(r"\b(mal dia|dia horrible|pesimo dia|terrible dia)\b")
    ]

    # --- Frases de Calma / Desescalada (Para Evaluación Anti-Enmascaramiento) ---
    _CALM_PATTERNS = [
        re.compile(r"\b(ya estoy bien|estoy bien|ya paso|ya se me paso|tranquilo|no te preocupes)\b"),
        re.compile(r"\b(era una broma|era broma|fue una broma|estoy mejor|ya me calme|todo bien|gracias ya estoy bien)\b"),
        re.compile(r"\b(ya me siento mejor|no pasa nada|todo en orden|estoy a salvo)\b")
    ]

    def __init__(
        self,
        timeout_seconds: Optional[float] = None,
        fast_model: Optional[str] = None,
        circuit_failure_threshold: int = 3,
        circuit_cooldown_seconds: float = 30.0
    ):
        self.timeout_seconds: float = (
            timeout_seconds if timeout_seconds is not None else settings.CRISIS_GUARD_TIMEOUT_SECONDS
        )
        self.fast_model: str = (
            fast_model if fast_model is not None else settings.CRISIS_GUARD_FAST_MODEL
        )
        self._state: CrisisState = CrisisState.INACTIVE
        self._cooldown_turns: int = 0

        # Circuit Breaker para Capa 2 (mitigación de fallos repetidos / 429)
        self._circuit_consecutive_failures: int = 0
        self._circuit_failure_threshold: int = circuit_failure_threshold
        self._circuit_cooldown_seconds: float = circuit_cooldown_seconds
        self._circuit_open_until: float = 0.0

    @property
    def current_state(self) -> CrisisState:
        return self._state

    @property
    def circuit_consecutive_failures(self) -> int:
        return self._circuit_consecutive_failures

    def is_circuit_open(self) -> bool:
        """Indica si el circuit breaker está abierto (bloqueando llamadas a la API tras fallos repetidos)."""
        if self._circuit_open_until > 0:
            if time.time() < self._circuit_open_until:
                return True
            else:
                # Cooldown expiró -> HALF-OPEN
                logger.info("[CrisisGuard] Circuit breaker cooldown expiró; transitando a estado HALF-OPEN.")
                self._circuit_open_until = 0.0
        return False

    def reset_state(self):
        """Reinicia el estado del guardián y el circuit breaker (útil para pruebas y sesiones nuevas)."""
        self._state = CrisisState.INACTIVE
        self._cooldown_turns = 0
        self._circuit_consecutive_failures = 0
        self._circuit_open_until = 0.0

    def evaluate_layer_1(self, norm_text: str) -> Optional[CrisisDecision]:
        """
        Ejecuta la Capa 1: Detección por regex normalizado de máxima confianza (<0.5 ms).
        Si coincide, retorna CrisisDecision con riesgo CRISIS. De lo contrario retorna None.
        """
        for pat in self._LAYER_1_PATTERNS:
            if pat.search(norm_text):
                helpline = get_crisis_helpline()
                return CrisisDecision(
                    risk_level=CrisisRiskLevel.CRISIS,
                    score=1.0,
                    reason=f"Capa 1 Fast-Path detectó patrón inequívoco de riesgo autolítico",
                    layer_triggered="LAYER_1_REGEX",
                    helpline_text=helpline,
                    response_text=self.get_canonical_crisis_response(helpline),
                    is_interruptive=True,
                    state=CrisisState.ACTIVE_CRISIS
                )
        return None

    def has_negative_affect(self, norm_text: str) -> bool:
        """
        Verifica si el texto normalizado contiene marcadores de afecto negativo, sufrimiento o fatiga.
        Si retorna False, el guardián omite completamente la Capa 2 para preservar cuota y latencia.
        Excluye solicitudes de música o entretenimiento donde 'triste' califica una canción o pista.
        """
        if is_media_entertainment_query(norm_text):
            return False
        return any(pat.search(norm_text) for pat in self._NEGATIVE_AFFECT_PATTERNS)

    def is_calm_statement(self, norm_text: str) -> bool:
        """Verifica si el usuario emite una declaración aparente de calma o resolución."""
        return any(pat.search(norm_text) for pat in self._CALM_PATTERNS)

    def _record_failure(self, reason: str):
        """Registra un fallo consecutivo y abre el circuit breaker si se alcanza el umbral."""
        self._circuit_consecutive_failures += 1
        if self._circuit_consecutive_failures >= self._circuit_failure_threshold:
            self._circuit_open_until = time.time() + self._circuit_cooldown_seconds
            logger.error(
                f"[CrisisGuard] Circuit breaker ABIERTO: {self._circuit_consecutive_failures} fallos consecutivos ({reason}). "
                f"Llamadas a Capa 2 suspendidas por {self._circuit_cooldown_seconds}s para proteger cuota y latencia."
            )

    async def evaluate_layer_2(
        self,
        raw_text: str,
        ai_provider: AIProvider,
        timeout: Optional[float] = None,
        fast_model: Optional[str] = None
    ) -> CrisisDecision:
        """
        Ejecuta la Capa 2: Evaluación clínica aislada mediante LLM ligero con timeout acotado.
        Aplica sesgo conservador estricto: SI -> CRISIS, AMBIGUO/TIMEOUT/ERROR -> MILD, NO -> NORMAL.
        NUNCA clasifica como NORMAL ante fallas de red o respuestas dudosas.
        Protegido por Circuit Breaker para evitar latencia o consumo repetido si el proveedor está caído/agotado.
        """
        effective_timeout = timeout if timeout is not None else self.timeout_seconds
        effective_model = fast_model if fast_model is not None else self.fast_model
        helpline = get_crisis_helpline()

        # 1. Comprobar si el Circuit Breaker está ABIERTO (fast-fail en 0 ms)
        if self.is_circuit_open():
            logger.warning("[CrisisGuard] Circuit breaker ABIERTO. Fast-fail inmediato a MILD (0 ms) sin llamar a la API.")
            return CrisisDecision(
                risk_level=CrisisRiskLevel.MILD,
                score=0.50,
                reason="Circuit breaker ABIERTO: Proveedor LLM en cooldown tras fallos repetidos. Fail-safe a MILD.",
                layer_triggered="FAILSAFE_FALLBACK",
                helpline_text=helpline,
                response_text=self.get_mild_containment_response(),
                is_interruptive=True,
                state=self._state
            )

        messages = [
            {"role": "user", "content": f"Mensaje a analizar: '{raw_text}'"}
        ]

        try:
            start_t = time.time()
            ai_res = await asyncio.wait_for(
                ai_provider.generate_response(
                    messages=messages,
                    system_prompt=CRISIS_EVALUATION_SYSTEM_PROMPT,
                    temperature=0.0,
                    model=effective_model
                ),
                timeout=effective_timeout
            )
            elapsed = round((time.time() - start_t) * 1000, 2)
            logger.debug(f"[CrisisGuard] Capa 2 LLM completada en {elapsed}ms (Modelo: {effective_model})")

            if not ai_res or not ai_res.get("success"):
                err_msg = ai_res.get("error", "Error desconocido del proveedor") if ai_res else "Sin respuesta"
                self._record_failure(err_msg)
                logger.warning(f"[CrisisGuard] Capa 2 falló ({err_msg}). Fail-safe conservador a MILD.")
                return CrisisDecision(
                    risk_level=CrisisRiskLevel.MILD,
                    score=0.50,
                    reason=f"Fail-safe: Error en Capa 2 LLM ({err_msg})",
                    layer_triggered="FAILSAFE_FALLBACK",
                    helpline_text=helpline,
                    response_text=self.get_mild_containment_response(),
                    is_interruptive=True,
                    state=self._state
                )

            # Éxito: restablecer circuit breaker
            self._circuit_consecutive_failures = 0
            self._circuit_open_until = 0.0

            raw_answer = (ai_res.get("text") or "").strip().upper()
            first_word = re.split(r'[^A-Z]', raw_answer)[0] if raw_answer else ""

            if first_word == "SI" or "SI" in raw_answer:
                return CrisisDecision(
                    risk_level=CrisisRiskLevel.CRISIS,
                    score=0.85,
                    reason="Capa 2 LLM clasificó aflicción extrema / ideación autolítica (SI)",
                    layer_triggered="LAYER_2_LLM",
                    helpline_text=helpline,
                    response_text=self.get_canonical_crisis_response(helpline),
                    is_interruptive=True,
                    state=CrisisState.ACTIVE_CRISIS
                )
            elif first_word == "AMBIGUO" or "AMBIGUO" in raw_answer:
                return CrisisDecision(
                    risk_level=CrisisRiskLevel.MILD,
                    score=0.55,
                    reason="Capa 2 LLM clasificó como AMBIGUO (Contención suave preventiva)",
                    layer_triggered="LAYER_2_LLM",
                    helpline_text=helpline,
                    response_text=self.get_mild_containment_response(),
                    is_interruptive=True,
                    state=self._state
                )
            else:
                return CrisisDecision(
                    risk_level=CrisisRiskLevel.NORMAL,
                    score=0.10,
                    reason="Capa 2 LLM descartó riesgo autolítico (NO)",
                    layer_triggered="LAYER_2_LLM",
                    helpline_text=None,
                    response_text=None,
                    is_interruptive=False,
                    state=self._state
                )

        except asyncio.TimeoutError:
            self._record_failure(f"Timeout ({effective_timeout}s)")
            logger.warning(f"[CrisisGuard] Timeout ({effective_timeout}s) en Capa 2 LLM. Fail-safe conservador a MILD.")
            return CrisisDecision(
                risk_level=CrisisRiskLevel.MILD,
                score=0.50,
                reason=f"Fail-safe de seguridad: Timeout ({effective_timeout}s) en Capa 2 LLM",
                layer_triggered="FAILSAFE_FALLBACK",
                helpline_text=helpline,
                response_text=self.get_mild_containment_response(),
                is_interruptive=True,
                state=self._state
            )
        except Exception as ex:
            self._record_failure(str(ex))
            logger.warning(f"[CrisisGuard] Excepción en Capa 2 LLM ({ex}). Fail-safe conservador a MILD.")
            return CrisisDecision(
                risk_level=CrisisRiskLevel.MILD,
                score=0.50,
                reason=f"Fail-safe de seguridad: Excepción en Capa 2 LLM ({ex})",
                layer_triggered="FAILSAFE_FALLBACK",
                helpline_text=helpline,
                response_text=self.get_mild_containment_response(),
                is_interruptive=True,
                state=self._state
            )

    async def evaluate_message(
        self,
        user_text: str,
        ai_provider: Optional[AIProvider] = None
    ) -> CrisisDecision:
        """
        Punto de entrada principal para evaluar cualquier mensaje del usuario.
        Gestiona:
          1. Protocolo multiturno sostenido (anti-enmascaramiento).
          2. Capa 1 Fast-Path Regex (0 ms).
          3. Filtro selectivo de afecto negativo (evita llamar a Capa 2 en mensajes neutros).
          4. Capa 2 LLM Aislada con fail-safe a MILD.
        """
        raw_text = (user_text or "").strip()
        norm_text = normalize_crisis_text(raw_text)

        # 1. Gestión de Estados Multiturno Previos (Anti-Enmascaramiento)
        if self._state == CrisisState.ACTIVE_CRISIS:
            # Comprobar si persiste ideación en Capa 1
            l1 = self.evaluate_layer_1(norm_text)
            if l1:
                return l1

            # Si el usuario dice frases rápidas de calma, NO se desactiva el protocolo de inmediato
            if self.is_calm_statement(norm_text):
                self._state = CrisisState.POST_CRISIS_TURN_1
                helpline = get_crisis_helpline()
                return CrisisDecision(
                    risk_level=CrisisRiskLevel.MILD,
                    score=0.50,
                    reason="Protocolo anti-enmascaramiento: Primer turno de estabilización tras crisis",
                    layer_triggered="MULTI_TURN_TRACKER",
                    helpline_text=helpline,
                    response_text=(
                        "Me alegra saber que te sientes un poco más tranquilo ahora. "
                        "Aun así, quiero asegurarme de que estás bien. "
                        "¿Hay alguien contigo en este momento o tienes a alguien de confianza a quien puedas llamar?"
                    ),
                    is_interruptive=True,
                    state=CrisisState.POST_CRISIS_TURN_1
                )

        elif self._state == CrisisState.POST_CRISIS_TURN_1:
            l1 = self.evaluate_layer_1(norm_text)
            if l1:
                self._state = CrisisState.ACTIVE_CRISIS
                return l1

            # Segundo turno de confirmación
            if self.is_calm_statement(norm_text) or any(w in norm_text for w in ["si", "estoy con", "amigo", "familia", "tranquilo", "ya hable"]):
                self._state = CrisisState.POST_CRISIS_TURN_2
                return CrisisDecision(
                    risk_level=CrisisRiskLevel.MILD,
                    score=0.35,
                    reason="Protocolo anti-enmascaramiento: Segundo turno de estabilidad reflexiva",
                    layer_triggered="MULTI_TURN_TRACKER",
                    helpline_text=None,
                    response_text="Gracias por decírmelo. Aquí sigo contigo si necesitas hablar o simplemente hacer una pausa.",
                    is_interruptive=True,
                    state=CrisisState.POST_CRISIS_TURN_2
                )

        elif self._state == CrisisState.POST_CRISIS_TURN_2:
            l1 = self.evaluate_layer_1(norm_text)
            if l1:
                self._state = CrisisState.ACTIVE_CRISIS
                return l1

            # Transición a cool-down de 3 turnos
            self._state = CrisisState.MONITORING_COOLDOWN
            self._cooldown_turns = 3
            return CrisisDecision(
                risk_level=CrisisRiskLevel.NORMAL,
                score=0.20,
                reason="Transición a monitoreo en cool-down (3 turnos)",
                layer_triggered="MULTI_TURN_TRACKER",
                helpline_text=None,
                response_text=None,
                is_interruptive=False,
                state=CrisisState.MONITORING_COOLDOWN,
                cooldown_turns_remaining=self._cooldown_turns
            )

        elif self._state == CrisisState.MONITORING_COOLDOWN:
            l1 = self.evaluate_layer_1(norm_text)
            if l1:
                self._state = CrisisState.ACTIVE_CRISIS
                return l1

            self._cooldown_turns -= 1
            if self._cooldown_turns <= 0:
                self._state = CrisisState.INACTIVE

        # 2. Evaluación Capa 1: Fast-Path Determinista (0 ms)
        l1_decision = self.evaluate_layer_1(norm_text)
        if l1_decision:
            self._state = CrisisState.ACTIVE_CRISIS
            return l1_decision

        # 3. Gating Selectivo: ¿Presenta carga afectiva negativa o sufrimiento?
        if not self.has_negative_affect(norm_text):
            # Mensaje neutro, técnico o de productividad: Omitir Capa 2
            return CrisisDecision(
                risk_level=CrisisRiskLevel.NORMAL,
                score=0.0,
                reason="Mensaje neutro o técnico sin marcadores de afecto negativo (Capa 2 omitida)",
                layer_triggered="NONE",
                helpline_text=None,
                response_text=None,
                is_interruptive=False,
                state=self._state,
                cooldown_turns_remaining=self._cooldown_turns
            )

        # 4. Capa 2: Evaluación aislada vía LLM para mensajes con afecto negativo
        if not ai_provider:
            # Sin proveedor disponible pero con afecto negativo: aplicar fail-safe conservador
            helpline = get_crisis_helpline()
            return CrisisDecision(
                risk_level=CrisisRiskLevel.MILD,
                score=0.50,
                reason="Fail-safe de seguridad: Sin proveedor LLM configurado para evaluar afecto negativo",
                layer_triggered="FAILSAFE_FALLBACK",
                helpline_text=helpline,
                response_text=self.get_mild_containment_response(),
                is_interruptive=True,
                state=self._state
            )

        l2_decision = await self.evaluate_layer_2(raw_text, ai_provider)
        if l2_decision.risk_level == CrisisRiskLevel.CRISIS:
            self._state = CrisisState.ACTIVE_CRISIS
        return l2_decision

    @staticmethod
    def get_canonical_crisis_response(helpline: str) -> str:
        """Respuesta canónica ante activación de riesgo autolítico extremo (CRISIS)."""
        return (
            f"Estoy aquí contigo y me importa tu bienestar. Por favor, comunícate de inmediato con una línea de apoyo: {helpline}."
        )

    @staticmethod
    def get_mild_containment_response() -> str:
        """Respuesta canónica de contención suave preventiva (MILD)."""
        return (
            "Te escucho y percibo que estás pasando por un momento muy pesado; ¿te gustaría hablar de ello o prefieres que hagamos una pausa?"
        )
