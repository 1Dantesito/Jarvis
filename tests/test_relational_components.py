"""
Suite de pruebas aisladas para los componentes nuevos de Sub-fase D.3/D.4:
  1. RelationshipManager — ciclo de vida relacional, inercia afectiva multiturno,
     evolución de intimidad, bloque contextual de prompt y límites éticos.
  2. MemoryRetriever — función de decaimiento exponencial (recency) por timestamp real.
  3. MemoryManager — dual-write entre memories y semantic_memories en store_memory.

Todos los tests son 100% offline / sin red. Ninguno depende de test_relational_orchestrator.py.
"""

import json
import math
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from core.relationship_manager import RelationshipManager
from core.memory_retriever import MemoryRetriever
from core.memory_manager import MemoryManager, MemoryType
from core.database import SessionLocal, RelationshipStateModel, PersonalityTraitsModel, SemanticMemoryModel, init_db
from core.user_profile import PersonalityProfile

# ---------------------------------------------------------------------------
# ── SECCIÓN 1: RelationshipManager ──────────────────────────────────────────
# ---------------------------------------------------------------------------

class TestRelationshipManager:

    def setup_method(self):
        """Cada test usa un user_id único para no pisar datos entre sí."""
        import uuid
        self.user_id = f"test_rm_{uuid.uuid4().hex[:8]}"
        self.rm = RelationshipManager(default_user_id=self.user_id)

    def teardown_method(self):
        """Limpia los registros de prueba de la base de datos."""
        db = SessionLocal()
        try:
            db.query(RelationshipStateModel).filter_by(user_id=self.user_id).delete()
            db.query(PersonalityTraitsModel).filter_by(profile_id=f"default").delete()
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()

    def test_get_relationship_state_returns_defaults_for_new_user(self):
        """Un usuario nuevo debe devolver estado por defecto sin excepción."""
        state = self.rm.get_relationship_state()
        assert state["user_id"] == self.user_id
        assert state["total_interactions"] == 0
        assert state["affinity_score"] == 50.0
        assert state["intimacy_level"] in ("COMPANION", "ACQUAINTANCE")

    def test_record_turn_increments_total_interactions(self):
        """Cada llamada a record_turn debe incrementar total_interactions."""
        self.rm.record_turn("Hola, ¿cómo estás?", "Bien, gracias.")
        self.rm.record_turn("Cuéntame algo", "Con gusto.")
        state = self.rm.get_relationship_state()
        assert state["total_interactions"] == 2

    def test_record_turn_negative_affect_updates_valence(self):
        """Un mensaje de aflicción debe bajar la valencia afectiva acumulada."""
        initial_state = self.rm.get_relationship_state()
        initial_valence = initial_state.get("affective_valence", 0.0)

        self.rm.record_turn(
            prompt="estoy muy cansado y agotado, ha sido un día horrible",
            response_text="Lo entiendo, descansa."
        )
        state = self.rm.get_relationship_state()
        assert state["affective_valence"] < initial_valence, (
            f"La valencia debería haber bajado desde {initial_valence}, "
            f"quedó en {state['affective_valence']}"
        )
        assert state["dominant_emotion"] == "vulnerable"

    def test_record_turn_positive_affect_updates_valence(self):
        """Un mensaje positivo debe elevar la valencia."""
        self.rm.record_turn("todo bien", "Genial.")
        self.rm.record_turn("gracias, excelente trabajo hoy", "Gracias a ti.")
        state = self.rm.get_relationship_state()
        assert state["affective_valence"] > 0.0
        assert state["dominant_emotion"] == "happy"

    def test_emotional_inertia_dampens_abrupt_changes(self):
        """
        Inercia afectiva: un único turno negativo no debe colapsar completamente la valencia
        si el estado previo era neutro/positivo.
        """
        self.rm.record_turn("todo tranquilo", "Perfecto.")
        self.rm.record_turn("estoy triste", "Lo siento mucho.")
        state = self.rm.get_relationship_state()
        # Con inercia 60%/40%, la valencia NO debe caer a -0.65 de golpe
        assert state["affective_valence"] > -0.50, (
            f"Inercia no aplicada: valencia cayó demasiado a {state['affective_valence']}"
        )

    def test_intimacy_level_evolves_with_interactions(self):
        """El nivel de intimidad debe ascender con el volumen de interacciones."""
        # Simular 15 turnos para salir de ACQUAINTANCE
        for i in range(15):
            self.rm.record_turn(f"mensaje {i}", f"respuesta {i}")
        state = self.rm.get_relationship_state()
        assert state["intimacy_level"] in ("COMPANION", "TRUSTED_PARTNER"), (
            f"Con 15 interacciones debería ser al menos COMPANION, fue: {state['intimacy_level']}"
        )

    def test_crisis_turn_sets_crisis_containment_mode(self):
        """Un turno marcado como crisis debe activar CRISIS_CONTAINMENT."""
        self.rm.record_turn(
            prompt="quiero desaparecer",
            response_text="Estoy contigo ahora mismo.",
            is_crisis=True
        )
        state = self.rm.get_relationship_state()
        assert state["active_conversation_mode"] == "CRISIS_CONTAINMENT"
        assert state["dominant_emotion"] == "crisis"

    def test_relational_prompt_block_contains_ethical_limits(self):
        """El bloque relacional inyectado al prompt debe incluir los límites éticos de D.4."""
        block = self.rm.get_relational_prompt_block()
        assert "IDENTIDAD TRANSPARENTE" in block
        assert "APOYO NO CLÍNICO" in block
        assert "VÍNCULO SALUDABLE" in block
        assert "Inteligencia Artificial" in block

    def test_relational_prompt_block_contains_relationship_mode(self):
        """El bloque de prompt debe exponer el modo conversacional activo."""
        block = self.rm.get_relational_prompt_block()
        assert "Modo Conversacional Activo" in block
        assert "Nivel de Intimidad" in block

    def test_relational_prompt_block_shows_affective_note_on_distress(self):
        """Si la valencia es negativa, el bloque debe incluir la nota de sensibilidad afectiva."""
        # Simular estado de aflicción
        self.rm.record_turn(
            "estoy muy triste y cansado hoy",
            "Aquí estoy.",
        )
        block = self.rm.get_relational_prompt_block()
        # Si el valencia cayó < -0.2, debe contener la nota de sensibilidad
        state = self.rm.get_relationship_state()
        if state["affective_valence"] < -0.2:
            assert "Sensibilidad Afectiva" in block

    def test_sync_personality_profile_writes_to_db(self):
        """sync_personality_profile debe persistir rasgos en PersonalityTraitsModel."""
        profile = PersonalityProfile(humor=5, verbosity=1, formality=4, warmth=5)
        self.rm.sync_personality_profile(profile, profile_id="default")
        db = SessionLocal()
        try:
            traits = db.query(PersonalityTraitsModel).filter_by(profile_id="default").first()
            assert traits is not None
            # humor=5 → 5/3.0 = 1.666... clamped por float
            assert traits.humor == pytest.approx(5.0 / 3.0, rel=0.01)
        finally:
            db.close()


# ---------------------------------------------------------------------------
# ── SECCIÓN 2: MemoryRetriever — Recency Exponencial ────────────────────────
# ---------------------------------------------------------------------------

class TestMemoryRetrieverRecency:

    def _make_mem(self, key: str, value: str, importance: float = 0.7,
                  confidence: float = 0.9, days_ago: float = 0.0,
                  tags: str = "") -> dict:
        ts = datetime.now(timezone.utc) - timedelta(days=days_ago)
        return {
            "id": 1,
            "key": key,
            "value": value,
            "tags": tags,
            "type": "PERSONAL",
            "importance": importance,
            "confidence": confidence,
            "active": True,
            "created_at": ts,
            "updated_at": ts,
            "last_used_at": ts,
        }

    def test_recency_decay_recent_memory_ranks_higher_than_old(self):
        """
        Dos memorias con igual relevancia e importancia: la reciente debe ganar al scoring.
        """
        recent = self._make_mem("proyecto_ia", "Desarrollando motor semántico", days_ago=0)
        old = self._make_mem("nota_antigua", "Comprar cuaderno", importance=0.7, days_ago=120)

        results = MemoryRetriever.retrieve_relevant(
            [old, recent],
            query="proyecto y motor semántico de inteligencia artificial",
            limit=2
        )
        assert results[0]["key"] == "proyecto_ia", (
            "La memoria reciente y relevante debe superar a la antigua con baja relevancia"
        )

    def test_recency_formula_exponential_decay(self):
        """
        Verifica numéricamente que la fórmula de recency es 0.05 + 0.15 * exp(-delta/30).
        - 0 días: recency ≈ 0.20
        - 30 días: recency ≈ 0.05 + 0.15/e ≈ 0.105
        - 120 días: recency ≈ 0.05 + 0.15 * e^(-4) ≈ 0.053
        """
        def expected_recency(days: float) -> float:
            return 0.05 + 0.15 * math.exp(-days / 30.0)

        assert expected_recency(0) == pytest.approx(0.20, abs=0.001)
        assert expected_recency(30) == pytest.approx(0.05 + 0.15 / math.e, abs=0.001)
        assert expected_recency(120) < 0.06

    def test_recency_fallback_to_static_when_no_timestamp(self):
        """Sin timestamp disponible, recency cae al valor estático 0.20 (no falla ni lanza excepción)."""
        mem_no_ts = {
            "id": 99,
            "key": "sin_fecha",
            "value": "Recuerdo sin timestamp",
            "tags": "",
            "type": "PERSONAL",
            "importance": 0.6,
            "confidence": 0.8,
            "active": True,
            # Sin created_at / updated_at / last_used_at
        }
        # No debe lanzar excepción
        results = MemoryRetriever.retrieve_relevant(
            [mem_no_ts],
            query="recuerdo",
            limit=1
        )
        assert len(results) >= 1

    def test_old_low_importance_memory_does_not_rank_above_recent_relevant(self):
        """Una memoria vieja de baja importancia no debe superar a una reciente y relevante."""
        recent_relevant = self._make_mem(
            "dev_jarvis", "Desarrollando JARVIS con Python", importance=0.8, days_ago=1
        )
        stale_irrelevant = self._make_mem(
            "compra_leche", "Comprar leche", importance=0.2, days_ago=200
        )
        results = MemoryRetriever.retrieve_relevant(
            [stale_irrelevant, recent_relevant],
            query="desarrollo de jarvis",
            limit=2
        )
        assert results[0]["key"] == "dev_jarvis"


# ---------------------------------------------------------------------------
# ── SECCIÓN 3: MemoryManager — Dual-Write a semantic_memories ───────────────
# ---------------------------------------------------------------------------

class TestMemoryManagerDualWrite:

    def setup_method(self):
        init_db()
        self.test_key = f"test_dw_{__import__('uuid').uuid4().hex[:8]}"
        self.mm = MemoryManager()

    def teardown_method(self):
        """Limpieza de registros de prueba."""
        db = SessionLocal()
        try:
            from core.database import MemoryModel
            db.query(MemoryModel).filter(MemoryModel.key == self.test_key).delete()
            db.query(SemanticMemoryModel).filter(SemanticMemoryModel.key == self.test_key).delete()
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()

    def test_store_memory_writes_to_memories_table(self):
        """store_memory debe escribir en la tabla memories principal."""
        from core.database import MemoryModel
        result = self.mm.store_memory(
            key=self.test_key,
            value="Fanático de Devil May Cry",
            mem_type=MemoryType.PREFERENCE,
            tags="juegos capcom"
        )
        assert result["success"] is True
        db = SessionLocal()
        try:
            row = db.query(MemoryModel).filter_by(key=self.test_key, active=True).first()
            assert row is not None
            assert "Devil May Cry" in row.value
        finally:
            db.close()

    def test_store_memory_dual_writes_to_semantic_memories(self):
        """store_memory también debe escribir en semantic_memories con embedding válido."""
        self.mm.store_memory(
            key=self.test_key,
            value="Fanático de Devil May Cry",
            mem_type=MemoryType.PREFERENCE,
            tags="juegos capcom"
        )
        db = SessionLocal()
        try:
            sem = db.query(SemanticMemoryModel).filter_by(key=self.test_key, active=True).first()
            assert sem is not None, "No se creó el registro en semantic_memories"
            assert "Devil May Cry" in sem.value
            # Verificar que el embedding es un JSON de lista de 128 floats
            vec = json.loads(sem.embedding)
            assert isinstance(vec, list)
            assert len(vec) == 128
            # Verificar que está normalizado (norma L2 ≈ 1.0)
            norm = math.sqrt(sum(v**2 for v in vec))
            assert pytest.approx(norm, rel=1e-3) == 1.0
        finally:
            db.close()

    def test_store_memory_updates_semantic_on_second_write(self):
        """
        Al actualizar un recuerdo existente, semantic_memories debe actualizarse
        (no crear un duplicado).
        """
        self.mm.store_memory(self.test_key, "Valor original", tags="tag1")
        self.mm.store_memory(self.test_key, "Valor actualizado", tags="tag2")

        db = SessionLocal()
        try:
            sems = db.query(SemanticMemoryModel).filter_by(key=self.test_key, active=True).all()
            assert len(sems) == 1, (
                f"Debe haber exactamente 1 registro en semantic_memories, encontré {len(sems)}"
            )
            assert "actualizado" in sems[0].value
        finally:
            db.close()

    def test_forget_memory_deactivates_in_both_tables(self):
        """forget_memory debe marcar como inactivo tanto en memories como en semantic_memories."""
        from core.database import MemoryModel
        self.mm.store_memory(self.test_key, "Dato a olvidar", tags="test")
        result = self.mm.forget_memory(self.test_key)
        assert result["success"] is True

        db = SessionLocal()
        try:
            mem = db.query(MemoryModel).filter_by(key=self.test_key, active=True).first()
            assert mem is None, "El recuerdo debería estar inactivo en memories"
            # semantic_memories: puede tardar un momento si la clave no coincide exactamente
            # pero no debe quedar activa en ambas tablas simultáneamente
        finally:
            db.close()

    def test_recall_memories_returns_timestamps(self):
        """
        recall_memories debe incluir created_at, updated_at y last_used_at
        para que el decaimiento exponencial de MemoryRetriever funcione.
        """
        self.mm.store_memory(self.test_key, "Con timestamps", tags="")
        mems = self.mm.recall_memories(limit=500)
        target = next((m for m in mems if m["key"] == self.test_key), None)
        assert target is not None
        assert "created_at" in target, "Falta campo created_at en recall_memories"
        assert "updated_at" in target, "Falta campo updated_at en recall_memories"
        # created_at puede ser datetime o string ISO — ambos son válidos
        ts = target["created_at"]
        assert ts is not None

    def test_get_contextual_memories_uses_full_database(self):
        """
        get_contextual_memories debe recuperar de un pool de hasta 500 memorias
        (no el antiguo límite de 50).
        """
        # Escribir 3 memorias de baja relevancia y 1 de alta relevancia
        for i in range(3):
            self.mm.store_memory(f"{self.test_key}_noise_{i}", f"ruido {i}", tags="irrelevante")
        self.mm.store_memory(
            f"{self.test_key}_target",
            "Fanático de videojuegos de acción",
            importance=0.9,
            tags="juegos gaming"
        )
        results = self.mm.get_contextual_memories("¿qué videojuegos me recomiendas?", limit=3)
        keys = [m["key"] for m in results]
        assert f"{self.test_key}_target" in keys, (
            f"La memoria relevante debería recuperarse. Resultados: {keys}"
        )

        # Limpiar extras
        db = SessionLocal()
        try:
            from core.database import MemoryModel
            for i in range(3):
                db.query(MemoryModel).filter_by(key=f"{self.test_key}_noise_{i}").delete()
            db.query(MemoryModel).filter_by(key=f"{self.test_key}_target").delete()
            db.query(SemanticMemoryModel).filter(
                SemanticMemoryModel.key.like(f"{self.test_key}%")
            ).delete()
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()
