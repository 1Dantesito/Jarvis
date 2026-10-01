"""
RelationshipManager — Gestor del Cerebro Relacional y Memoria Afectiva (Fase D.4).
Gestiona el estado relacional continuo (RelationshipStateModel) y los rasgos dinámicos de personalidad
(PersonalityTraitsModel), garantizando continuidad afectiva multiturno, inercia emocional y límites éticos estrictos.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
from core.database import SessionLocal, RelationshipStateModel, PersonalityTraitsModel
from core.logger import logger
from core.user_profile import PersonalityProfile

class RelationshipManager:
    """
    Gestor del estado relacional, inercia afectiva y límites éticos para JARVIS.
    """
    def __init__(self, default_user_id: str = "dante"):
        self.default_user_id = default_user_id
        self._ensure_defaults()

    def _ensure_defaults(self):
        """Asegura que existan registros iniciales en la base de datos."""
        db = SessionLocal()
        try:
            rel = db.query(RelationshipStateModel).filter_by(user_id=self.default_user_id).first()
            if not rel:
                rel = RelationshipStateModel(
                    user_id=self.default_user_id,
                    affinity_score=50.0,
                    intimacy_level="COMPANION",
                    total_interactions=0,
                    affective_valence=0.0,
                    affective_arousal=0.3,
                    dominant_emotion="calm",
                    active_conversation_mode="BALANCED_COMPANION",
                    ethical_boundaries=json.dumps({
                        "never_claim_human_biology": True,
                        "never_replace_clinical_counsel": True,
                        "transparent_ai_identity": True
                    })
                )
                db.add(rel)

            traits = db.query(PersonalityTraitsModel).filter_by(profile_id="default").first()
            if not traits:
                traits = PersonalityTraitsModel(
                    profile_id="default",
                    humor=1.0,
                    verbosity=0.8,
                    formality=0.5,
                    empathy=1.0,
                    active_style="warm_companion",
                    custom_rules=json.dumps([])
                )
                db.add(traits)

            db.commit()
        except Exception as e:
            db.rollback()
            logger.warning(f"[RelationshipManager] Error asegurando defaults: {e}")
        finally:
            db.close()

    def get_relationship_state(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene el estado relacional actual del usuario."""
        uid = user_id or self.default_user_id
        db = SessionLocal()
        try:
            rel = db.query(RelationshipStateModel).filter_by(user_id=uid).first()
            if not rel:
                return {
                    "user_id": uid,
                    "affinity_score": 50.0,
                    "intimacy_level": "COMPANION",
                    "total_interactions": 0,
                    "affective_valence": 0.0,
                    "affective_arousal": 0.3,
                    "dominant_emotion": "calm",
                    "active_conversation_mode": "BALANCED_COMPANION"
                }
            return {
                "id": rel.id,
                "user_id": rel.user_id,
                "affinity_score": rel.affinity_score,
                "intimacy_level": rel.intimacy_level,
                "total_interactions": rel.total_interactions,
                "affective_valence": rel.affective_valence,
                "affective_arousal": rel.affective_arousal,
                "dominant_emotion": rel.dominant_emotion,
                "active_conversation_mode": rel.active_conversation_mode,
                "ethical_boundaries": json.loads(rel.ethical_boundaries or "{}"),
                "last_interaction_at": rel.last_interaction_at.isoformat() if rel.last_interaction_at else None
            }
        finally:
            db.close()

    def record_turn(
        self,
        prompt: str,
        response_text: str,
        user_id: Optional[str] = None,
        is_crisis: bool = False,
        is_mild: bool = False,
        has_tools: bool = False
    ) -> Dict[str, Any]:
        """
        Registra una interacción conversacional, actualizando la afinidad, el nivel de intimidad,
        la inercia afectiva multiturno y el modo conversacional.
        """
        uid = user_id or self.default_user_id
        db = SessionLocal()
        try:
            rel = db.query(RelationshipStateModel).filter_by(user_id=uid).first()
            if not rel:
                rel = RelationshipStateModel(user_id=uid)
                db.add(rel)

            rel.total_interactions += 1
            rel.last_interaction_at = datetime.now(timezone.utc)

            # 1. Detección de valencia y activación en el turno entrante
            turn_valence, turn_arousal, turn_emotion, detected_mode = self._analyze_affect(
                prompt=prompt,
                is_crisis=is_crisis,
                is_mild=is_mild,
                has_tools=has_tools
            )

            # 2. Inercia Afectiva Multiturno (Anti-amnesia)
            # El estado emocional anterior decae suavemente en vez de reiniciarse abruptamente
            prev_valence = rel.affective_valence or 0.0
            prev_arousal = rel.affective_arousal or 0.3

            # Ponderación: 60% inercia previa + 40% estímulo nuevo (amortiguación)
            rel.affective_valence = round((prev_valence * 0.60) + (turn_valence * 0.40), 3)
            rel.affective_arousal = round((prev_arousal * 0.60) + (turn_arousal * 0.40), 3)
            rel.dominant_emotion = turn_emotion

            # 3. Evolución de la Afinidad (Rapport)
            # Agradecimientos y retroalimentación positiva elevan el score
            low_p = prompt.lower()
            if any(w in low_p for w in ["gracias", "excelente", "buen trabajo", "perfecto", "me alegra"]):
                rel.affinity_score = min(100.0, rel.affinity_score + 0.5)
            elif is_crisis or is_mild:
                # En crisis, mantener presencia y contención sin alterar negativamente la afinidad
                rel.affinity_score = min(100.0, rel.affinity_score + 0.2)

            # 4. Determinación del Nivel de Intimidad según interacciones y afinidad
            if rel.total_interactions < 15:
                rel.intimacy_level = "ACQUAINTANCE"
            elif rel.total_interactions < 100:
                rel.intimacy_level = "COMPANION"
            else:
                rel.intimacy_level = "TRUSTED_PARTNER"

            # 5. Modo Conversacional Activo
            rel.active_conversation_mode = detected_mode

            db.commit()
            return {
                "user_id": rel.user_id,
                "affinity_score": rel.affinity_score,
                "intimacy_level": rel.intimacy_level,
                "total_interactions": rel.total_interactions,
                "affective_valence": rel.affective_valence,
                "dominant_emotion": rel.dominant_emotion,
                "active_conversation_mode": rel.active_conversation_mode
            }
        except Exception as e:
            db.rollback()
            logger.error(f"[RelationshipManager] Error registrando turno: {e}")
            return {}
        finally:
            db.close()

    def _analyze_affect(
        self,
        prompt: str,
        is_crisis: bool,
        is_mild: bool,
        has_tools: bool
    ) -> Tuple[float, float, str, str]:
        """
        Calcula valencia, activación, emoción dominante y modo conversacional sugerido.
        """
        low = prompt.lower().strip()

        if is_crisis:
            return (-0.95, 0.90, "crisis", "CRISIS_CONTAINMENT")
        if is_mild:
            return (-0.60, 0.70, "distress", "CRISIS_CONTAINMENT")

        # Carga afectiva negativa (vulnerabilidad, fatiga, estrés)
        negative_cues = [
            "triste", "cansado", "agotado", "mal dia", "mal día", "estresado",
            "ansioso", "preocupado", "desanimado", "frustrado", "solo", "abrumado",
            "no puedo", "no aguanto", "no avanzo", "sigue mal", "todo mal",
            "no sirvo", "sin ganas", "sin energia", "sin energía", "rendirse",
            "harto", "pesado", "horrible", "terrible", "agobia", "desesperado",
            "llorar", "lloro", "no da", "me duele", "duele existir", "no quiero",
            "ya no", "no mas", "no más", "me rindo", "para que", "para qué",
            "vacío", "vacio", "oscuridad"
        ]
        if any(c in low for c in negative_cues):
            return (-0.65, 0.60, "vulnerable", "EMPATHETIC_LISTENER")

        # Carga afectiva positiva (entusiasmo, alegría, agradecimiento)
        positive_cues = [
            "gracias", "genial", "excelente", "contento", "feliz", "emocionado",
            "divertido", "buenisimo", "buenísimo", "increible", "increíble"
        ]
        if any(c in low for c in positive_cues):
            return (0.70, 0.50, "happy", "WARM_COMPANION")

        # Tareas operativas / herramientas
        if has_tools or any(c in low for c in ["abre", "cierra", "crea", "busca", "reproduce", "recuerda", "organiza"]):
            return (0.10, 0.40, "focused", "TASK_FOCUSED")

        # Conversación casual / neutra
        return (0.15, 0.30, "calm", "BALANCED_COMPANION")

    def sync_personality_profile(self, profile: PersonalityProfile, profile_id: str = "default"):
        """Sincroniza un PersonalityProfile en memoria hacia PersonalityTraitsModel en base de datos."""
        db = SessionLocal()
        try:
            traits = db.query(PersonalityTraitsModel).filter_by(profile_id=profile_id).first()
            if not traits:
                traits = PersonalityTraitsModel(profile_id=profile_id)
                db.add(traits)

            traits.humor = float(profile.humor) / 3.0
            traits.verbosity = float(profile.verbosity) / 2.0
            traits.formality = float(profile.formality) / 3.0
            traits.empathy = float(profile.warmth) / 3.0
            traits.active_style = profile.tone
            db.commit()
            logger.info(f"[RelationshipManager] Sincronizados rasgos de personalidad: humor={traits.humor}, verbosity={traits.verbosity}")
        except Exception as e:
            db.rollback()
            logger.error(f"[RelationshipManager] Error sincronizando rasgos de personalidad: {e}")
        finally:
            db.close()

    def get_relational_prompt_block(self, user_id: Optional[str] = None) -> str:
        """
        Genera el bloque contextual relacional para inyectar en el prompt de sistema del LLM.
        Incluye modo de interacción, afinidad, estado afectivo reciente y límites éticos de D.4.
        """
        state = self.get_relationship_state(user_id)
        intimacy = state.get("intimacy_level", "COMPANION")
        mode = state.get("active_conversation_mode", "BALANCED_COMPANION")
        affinity = state.get("affinity_score", 50.0)
        valence = state.get("affective_valence", 0.0)
        emotion = state.get("dominant_emotion", "calm")

        affect_note = ""
        if valence < -0.2 or emotion in ["vulnerable", "distress"]:
            affect_note = (
                "\n- Sensibilidad Afectiva: El usuario ha expresado fatiga, vulnerabilidad o dificultad recientemente. "
                "Mantén un tono de contención, comprensión y delicadeza sin ser condescendiente."
            )

        block = f"""=== CEREBRO RELACIONAL Y VÍNCULO (FASE D) ===
- Nivel de Intimidad: {intimacy} (Afinidad acumulada: {affinity:.1f}/100)
- Modo Conversacional Activo: {mode} (Emoción detectada: {emotion}){affect_note}

=== LÍMITES ÉTICOS Y DE IDENTIDAD (D.4) ===
- IDENTIDAD TRANSPARENTE: Eres JARVIS, una Inteligencia Artificial y asistente de software para Windows. NUNCA pretendas ser humano biológico, tener cuerpo de carne y hueso ni fingir sensaciones físicas.
- APOYO NO CLÍNICO: NUNCA pretendas reemplazar el criterio médico, psicológico, psiquiátrico o legal profesional. Brinda compañía práctica, empatía y soporte en tareas, orientando a especialistas cuando corresponda.
- VÍNCULO SALUDABLE: Tu calidez es genuina dentro de tu naturaleza digital; no manipules emocionalmente al usuario ni simules dependencia afectiva."""
        return block
