import pytest
from tools.router import TOOL_REGISTRY, ToolType, ToolRouter
from core.social_layer import SocialResponseLayer
from core.user_profile import PersonalityProfile

def test_all_tools_classified():
    """Verifica que ninguna herramienta quede sin clasificar en TOOL_REGISTRY (BUG-24)."""
    assert len(TOOL_REGISTRY) >= 30
    for name, t_type in TOOL_REGISTRY.items():
        assert isinstance(t_type, ToolType)
        assert t_type in [ToolType.ACTION, ToolType.QUERY]

def test_query_tools_classification():
    assert TOOL_REGISTRY["list_reminders"] == ToolType.QUERY
    assert TOOL_REGISTRY["list_tasks"] == ToolType.QUERY
    assert TOOL_REGISTRY["get_pending_summary"] == ToolType.QUERY
    assert TOOL_REGISTRY["current_datetime"] == ToolType.QUERY
    assert TOOL_REGISTRY["get_running_applications"] == ToolType.QUERY
    assert TOOL_REGISTRY["search_files"] == ToolType.QUERY
    assert TOOL_REGISTRY["read_text_file"] == ToolType.QUERY

def test_action_tools_classification():
    assert TOOL_REGISTRY["create_reminder"] == ToolType.ACTION
    assert TOOL_REGISTRY["complete_reminder"] == ToolType.ACTION
    assert TOOL_REGISTRY["delete_reminder"] == ToolType.ACTION
    assert TOOL_REGISTRY["clear_all_pending"] == ToolType.ACTION
    assert TOOL_REGISTRY["play_music"] == ToolType.ACTION
    assert TOOL_REGISTRY["recommend_music"] == ToolType.ACTION
    assert TOOL_REGISTRY["open_application"] == ToolType.ACTION
    assert TOOL_REGISTRY["create_text_file"] == ToolType.ACTION

def test_list_reminders_empty_and_non_empty():
    personality = PersonalityProfile()
    
    # 1. Vacío -> mensaje explícito y natural
    res_empty = SocialResponseLayer.format_social_tool_phrase(
        tool_name="list_reminders",
        tool_args={},
        tool_result={"success": True, "data": {"reminders": []}},
        personality=personality
    )
    assert res_empty == "No tienes recordatorios pendientes por ahora."
    assert res_empty != "Acción completada con éxito."

    # 2. Con recordatorios -> detalla los títulos
    res_with_data = SocialResponseLayer.format_social_tool_phrase(
        tool_name="list_reminders",
        tool_args={},
        tool_result={"success": True, "data": {"reminders": [{"title": "Comprar pan"}, {"title": "Llamar al médico"}]}},
        personality=personality
    )
    assert "Comprar pan" in res_with_data
    assert "Llamar al médico" in res_with_data
    assert "2 recordatorios" in res_with_data

def test_list_tasks_empty_and_non_empty():
    personality = PersonalityProfile()
    
    res_empty = SocialResponseLayer.format_social_tool_phrase(
        tool_name="list_tasks",
        tool_args={},
        tool_result={"success": True, "data": {"tasks": []}},
        personality=personality
    )
    assert res_empty == "No tienes tareas pendientes por ahora."

    res_with_data = SocialResponseLayer.format_social_tool_phrase(
        tool_name="list_tasks",
        tool_args={},
        tool_result={"success": True, "data": {"tasks": [{"title": "Terminar reporte"}]}},
        personality=personality
    )
    assert "Terminar reporte" in res_with_data
