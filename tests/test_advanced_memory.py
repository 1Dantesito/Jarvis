import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from core.memory_manager import memory_manager, MemoryType
from core.user_profile import UserProfile, PersonalityProfile
from core.memory_retriever import MemoryRetriever
from core.orchestrator import JarvisOrchestrator
from providers.mock_provider import MockAIProvider

def test_memory_creation_and_fields():
    res = memory_manager.store_memory(
        key="test_rock_preference",
        value="Le encanta el rock clásico y alternativo",
        mem_type=MemoryType.MEDIA_PREFERENCE,
        importance=0.85,
        confidence=0.95
    )
    assert res["success"] is True
    assert res["key"] == "test_rock_preference"

    # Recuperar
    mems = memory_manager.recall_memories(mem_type=MemoryType.MEDIA_PREFERENCE)
    found = [m for m in mems if m["key"] == "test_rock_preference"]
    assert len(found) > 0
    assert found[0]["importance"] == 0.85

def test_contradiction_resolution_and_update():
    test_key = "test_contradiction_banda_tmp"
    # 1. Guarda valor inicial
    memory_manager.store_memory(key=test_key, value="Linkin Park")
    
    # 2. Actualiza con nueva declaración
    res = memory_manager.store_memory(key=test_key, value="Queen")
    assert res["success"] is True

    # 3. Verificar que solo hay 1 entrada activa actualizada
    mems = memory_manager.recall_memories(limit=100)
    active_keys = [m for m in mems if m["key"] == test_key]
    assert len(active_keys) == 1
    assert active_keys[0]["value"] == "Queen"

    # Limpiar
    memory_manager.forget_memory(test_key)

def test_forget_memory_and_categories():
    memory_manager.store_memory(key="hobby_temporal", value="Aprender ajedrez")
    
    # Olvidar
    res = memory_manager.forget_memory("hobby_temporal")
    assert res["success"] is True
    assert res["forgotten_count"] >= 1

    # Verificar que ya no aparece en activos
    active_mems = memory_manager.recall_memories()
    found = [m for m in active_mems if m["key"] == "hobby_temporal"]
    assert len(found) == 0

def test_contextual_retriever_ranking():
    mems = [
        {"key": "musica_metal", "value": "Escucha heavy metal al entrenar", "type": "MEDIA_PREFERENCE", "importance": 0.8, "confidence": 0.9, "active": True},
        {"key": "proyecto_grado", "value": "Trabajando en JARVIS con Python", "type": "PROJECT", "importance": 0.9, "confidence": 0.95, "active": True},
        {"key": "comida", "value": "Prefiere sushi", "type": "PREFERENCE", "importance": 0.3, "confidence": 0.8, "active": True}
    ]

    retrieved = MemoryRetriever.retrieve_relevant(mems, "Qué música me recomiendas", limit=2)
    assert len(retrieved) > 0
    assert retrieved[0]["key"] == "musica_metal"

def test_user_profile_and_personality_separation():
    prof = UserProfile(name="Dante", role="Developer")
    assert prof.name == "Dante"
    assert prof.personality.verbosity == 1
    assert "Ultra breve" in prof.personality.to_instruction()

def test_export_memory():
    exp = memory_manager.export_memory()
    assert "user_profile" in exp
    assert "memories" in exp
    assert "export_timestamp" in exp

@pytest.mark.asyncio
async def test_orchestrator_memory_flow():
    orch = JarvisOrchestrator(primary_provider=MockAIProvider())
    res = await orch.process_user_input("Recuerda que me gusta el rock")
    assert res["success"] is True
    tools = [t["tool_name"] for t in res["tools_executed"]]
    assert "remember_info" in tools
