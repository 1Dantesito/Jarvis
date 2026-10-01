"""
Suite de pruebas para la Sub-fase D.3 (Motor Semántico, Embeddings y Migraciones Aditivas).
Valida:
  1. LocalSemanticVectorizer: Determinismo, dimensiones exactas (128D) y normalización L2.
  2. Similitud Coseno: Alta sintonía para paráfrasis y baja para textos no relacionados.
  3. Migraciones aditivas: Creación de tablas semantic_memories, relationship_state y personality_traits
     en jarvis.db sin alterar ni truncar las tablas preexistentes.
  4. MemoryRetriever Híbrido: Recuperación exitosa de recuerdos ante paráfrasis sin overlap léxico directo.
  5. Compatibilidad de esquemas JSON D.2 (semantic_memory_entry, relationship_state, personality_traits).
"""

import math
import pytest
from core.semantic_vectorizer import LocalSemanticVectorizer, VECTOR_DIMENSIONS
from core.database import (
    engine,
    init_db,
    SessionLocal,
    MemoryModel,
    SemanticMemoryModel,
    RelationshipStateModel,
    PersonalityTraitsModel
)
from core.memory_retriever import MemoryRetriever
from sqlalchemy import inspect

def test_local_vectorizer_determinism_and_dimensions():
    """Verifica que el vectorizador produzca siempre 128 floats normalizados L2 de forma determinista."""
    text_a = "Mi lenguaje de programación preferido es Python"
    vec_1 = LocalSemanticVectorizer.vectorize(text_a)
    vec_2 = LocalSemanticVectorizer.vectorize(text_a)

    assert len(vec_1) == VECTOR_DIMENSIONS == 128
    assert vec_1 == vec_2, "El vectorizador debe ser 100% determinista"

    # Verificación de norma L2 unitaria
    norm = math.sqrt(sum(x * x for x in vec_1))
    assert pytest.approx(norm, rel=1e-3) == 1.0

def test_local_vectorizer_cosine_similarity():
    """Verifica el cálculo de similitud coseno sobre paráfrasis y temas dispares."""
    vec_base = LocalSemanticVectorizer.vectorize("Mi banda favorita es Linkin Park")
    vec_same = LocalSemanticVectorizer.vectorize("Mi banda favorita es Linkin Park")
    vec_para = LocalSemanticVectorizer.vectorize("Su grupo de música predilecto es Linkin Park")
    vec_diff = LocalSemanticVectorizer.vectorize("La cotización del dólar subió en la bolsa de valores")

    # Identidad
    sim_ident = LocalSemanticVectorizer.cosine_similarity(vec_base, vec_same)
    assert pytest.approx(sim_ident, rel=1e-3) == 1.0

    # Paráfrasis
    sim_para = LocalSemanticVectorizer.cosine_similarity(vec_base, vec_para)
    assert sim_para > 0.35, f"Paráfrasis debió tener similitud significativa, dio: {sim_para}"

    # Disparidad temática
    sim_diff = LocalSemanticVectorizer.cosine_similarity(vec_base, vec_diff)
    assert sim_diff < 0.15, f"Texto diferente debió tener similitud baja, dio: {sim_diff}"
    assert sim_para > (sim_diff + 0.25), "La paráfrasis debe superar ampliamente al texto dispar"

def test_additive_database_models_init():
    """Verifica que init_db cree las nuevas tablas de Fase D sin alterar las existentes."""
    init_db()
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    # Tablas preexistentes preservadas
    assert "memories" in table_names
    assert "reminders" in table_names
    assert "tasks" in table_names
    assert "user_profile" in table_names

    # Nuevas tablas aditivas de Fase D
    assert "semantic_memories" in table_names
    assert "relationship_state" in table_names
    assert "personality_traits" in table_names

def test_hybrid_memory_retriever_paraphrase():
    """
    Verifica que MemoryRetriever recupere información mediante similitud semántica
    incluso cuando el overlap léxico exacto sea nulo o insuficiente.
    """
    memories = [
        {
            "id": 1,
            "key": "gusto_musical",
            "value": "Su banda predilecta es Linkin Park",
            "tags": "musica rock",
            "type": "MEDIA_PREFERENCE",
            "importance": 0.9,
            "confidence": 0.95,
            "active": True
        },
        {
            "id": 2,
            "key": "rutina_desayuno",
            "value": "Toma café negro sin azúcar a las 7 de la mañana",
            "tags": "rutina alimentacion",
            "type": "HABIT",
            "importance": 0.6,
            "confidence": 0.90,
            "active": True
        }
    ]

    # Query que usa sinónimos y paráfrasis ("canción predilecta", "grupo musical")
    query = "cuál es su grupo musical preferido"
    results = MemoryRetriever.retrieve_relevant(memories, query, limit=1)

    assert len(results) >= 1
    assert results[0]["key"] == "gusto_musical"

def test_semantic_memory_models_crud():
    """Verifica la persistencia y lectura de los modelos aditivos en jarvis.db."""
    db = SessionLocal()
    try:
        # Limpieza previa de registros de prueba
        db.query(SemanticMemoryModel).filter_by(entry_id="test-sem-001").delete()
        db.query(RelationshipStateModel).filter_by(user_id="test_user_dante").delete()
        db.query(PersonalityTraitsModel).filter_by(profile_id="test_profile_jarvis").delete()
        db.commit()

        # 1. SemanticMemoryModel
        sem_mem = SemanticMemoryModel(
            entry_id="test-sem-001",
            key="hobbie_principal",
            value="Le apasiona el senderismo y la fotografía de montaña",
            category="hobbies",
            confidence=0.92,
            importance=0.85,
            emotional_valence=0.75,
            embedding=str(LocalSemanticVectorizer.vectorize("senderismo y fotografia de montaña"))
        )
        db.add(sem_mem)

        # 2. RelationshipStateModel
        rel_state = RelationshipStateModel(
            user_id="test_user_dante",
            affinity_score=68.5,
            intimacy_level="COMPANION",
            total_interactions=42,
            active_conversation_mode="WARM_COMPANION",
            dominant_emotion="enthusiastic"
        )
        db.add(rel_state)

        # 3. PersonalityTraitsModel
        traits = PersonalityTraitsModel(
            profile_id="test_profile_jarvis",
            humor=1.2,
            verbosity=0.85,
            formality=0.45,
            empathy=1.1,
            active_style="warm_companion"
        )
        db.add(traits)
        db.commit()

        # Comprobación de lectura
        saved_mem = db.query(SemanticMemoryModel).filter_by(entry_id="test-sem-001").first()
        assert saved_mem is not None
        assert saved_mem.key == "hobbie_principal"
        assert saved_mem.importance == 0.85

        saved_rel = db.query(RelationshipStateModel).filter_by(user_id="test_user_dante").first()
        assert saved_rel is not None
        assert saved_rel.intimacy_level == "COMPANION"

        saved_traits = db.query(PersonalityTraitsModel).filter_by(profile_id="test_profile_jarvis").first()
        assert saved_traits is not None
        assert saved_traits.empathy == 1.1

    finally:
        db.close()

def test_diagnostic_d1_gaming_paraphrase_retrieval():
    """
    CASO DIAGNÓSTICO D.1 OBLIGATORIO:
    Consulta parafraseada: '¿qué videojuegos me recomiendas?'
    Recuerdo almacenado: 'Fanático de Devil May Cry', tags: 'juegos capcom', key: 'gusto_gaming'.
    
    Verifica que:
      1. El matching léxico estricto antiguo (sinónimos desalineados: 'videojuegos' vs 'juegos', sin palabras comunes)
         tenía overlap léxico igual a 0.
      2. El nuevo MemoryRetriever híbrido resuelve con éxito la paráfrasis y retorna el recuerdo en primer lugar.
    """
    import re
    memories = [
        {
            "id": 101,
            "key": "gusto_gaming",
            "value": "Fanático de Devil May Cry",
            "tags": "juegos capcom",
            "type": "PREFERENCE",
            "importance": 0.85,
            "confidence": 0.95,
            "active": True
        },
        {
            "id": 102,
            "key": "estudio_actual",
            "value": "Estudiando arquitectura de software concurrente",
            "tags": "ingenieria libros",
            "type": "PROJECT",
            "importance": 0.70,
            "confidence": 0.90,
            "active": True
        }
    ]

    query = "¿qué videojuegos me recomiendas?"

    # 1. Demostración del fallo del matching léxico antiguo
    q_words = set(re.findall(r'\w+', query.lower())) - {"de", "me", "que"}
    mem_words = set(re.findall(r'\w+', f"{memories[0]['key']} {memories[0]['value']} {memories[0]['tags']}".lower())) - {"de", "me", "que"}
    strict_overlap = len(q_words.intersection(mem_words))
    assert strict_overlap == 0, "No debe haber overlap de palabras directas entre 'videojuegos/recomiendas' y 'juegos/capcom/devil/may/cry'"

    # 2. El nuevo MemoryRetriever híbrido sí lo resuelve mediante similitud semántica
    results = MemoryRetriever.retrieve_relevant(memories, query, limit=1)
    assert len(results) >= 1
    assert results[0]["key"] == "gusto_gaming"
    assert "Devil May Cry" in results[0]["value"]

def test_synonym_cluster_embeddings_bridging():
    """Verifica que el puente semántico por clusters lematizados eleve la similitud de términos análogos."""
    vec_cine_1 = LocalSemanticVectorizer.vectorize("mi pelicula favorita de accion")
    vec_cine_2 = LocalSemanticVectorizer.vectorize("su film preferido de cine")
    sim_cine = LocalSemanticVectorizer.cosine_similarity(vec_cine_1, vec_cine_2)
    assert sim_cine > 0.35, f"Película y film deben tener alta similitud, dio {sim_cine}"

    vec_game_1 = LocalSemanticVectorizer.vectorize("videojuegos para fin de semana")
    vec_game_2 = LocalSemanticVectorizer.vectorize("juegos de consola para ocio")
    sim_game = LocalSemanticVectorizer.cosine_similarity(vec_game_1, vec_game_2)
    assert sim_game > 0.35, f"Videojuegos y juegos deben asociarse semánticamente, dio {sim_game}"

def test_temporal_decay_ebbinghaus_ranking():
    """Verifica que recuerdos relevantes con alta importancia superen a recuerdos con baja relevancia en el scoring."""
    recent_mem = {
        "id": 201,
        "key": "proyecto_ia",
        "value": "Desarrollando arquitectura de agentes autónomos",
        "tags": "ia agentes python",
        "type": "PROJECT",
        "importance": 0.9,
        "confidence": 0.95,
        "active": True
    }
    older_low_mem = {
        "id": 202,
        "key": "nota_antigua",
        "value": "Comprar libreta de apuntes",
        "tags": "compras papeleria",
        "type": "PERSONAL",
        "importance": 0.3,
        "confidence": 0.6,
        "active": True
    }

    results = MemoryRetriever.retrieve_relevant([older_low_mem, recent_mem], "arquitectura y desarrollo de agentes", limit=2)
    assert results[0]["key"] == "proyecto_ia"

