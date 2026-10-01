import pytest
from core.memory_manager import memory_manager

def test_memory_profile():
    original_profile = memory_manager.get_all_profile()
    original_name = original_profile.get("name", "Dante")
    try:
        memory_manager.set_profile("name", "Dante")
        profile = memory_manager.get_all_profile()
        assert profile.get("name") == "Dante"
    finally:
        memory_manager.set_profile("name", original_name)

def test_memory_store_and_recall():
    res = memory_manager.store_memory("hobby", "Programar en Python", category="personal")
    assert res["success"] is True

    mems = memory_manager.recall_memories(category="personal")
    assert any(m["key"] == "hobby" and m["value"] == "Programar en Python" for m in mems)

def test_tasks_crud():
    res = memory_manager.create_task("Probar tareas CRUD temp", priority="HIGH")
    assert res["success"] is True
    assert res["data"]["id"] is not None
    t_id = res["data"]["id"]

    try:
        tasks = memory_manager.list_tasks()
        assert any(t["id"] == t_id for t in tasks)
    finally:
        memory_manager.delete_task(t_id)
