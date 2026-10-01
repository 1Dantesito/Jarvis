import pytest
from core.context_engine import ContextEngine

def test_datetime_dict():
    dt = ContextEngine.get_current_datetime_dict()
    assert "time_12h" in dt
    assert "time_24h" in dt
    assert "date" in dt
    assert "day_of_week" in dt
    assert "timezone" in dt
    assert dt["year"] >= 2026

def test_system_context_block():
    block = ContextEngine.build_system_context_block(
        user_profile={
            "name": "Jhonatan",
            "full_name": "Jhonatan David Torres Patiño",
            "age": "22",
            "music_taste": "Rock, Metal alternativo",
            "favorite_bands": ["MCR", "SOAD"]
        },
        pending_tasks_count=3
    )
    assert "Jhonatan David Torres Patiño" in block
    assert "MCR, SOAD" in block
    assert "Tareas pendientes activas: 3" in block
    assert "PERFIL DEL USUARIO" in block

