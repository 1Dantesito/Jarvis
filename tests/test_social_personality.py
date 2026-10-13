import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from core.user_profile import PersonalityProfile, UserProfile
from core.social_layer import SocialResponseLayer, ConversationState
from core.orchestrator import JarvisOrchestrator
from providers.mock_provider import MockAIProvider

def test_personality_style_adjustments():
    p = PersonalityProfile()
    assert p.verbosity == 1
    assert p.humor == 3

    # Feedback: más corto
    p.adjust_style("corto")
    assert p.verbosity == 1

    # Feedback: más divertido
    p.adjust_style("divertido")
    assert p.humor == 4
    assert p.playfulness == 4

    # Feedback: más serio
    p.adjust_style("serio")
    assert p.humor == 1
    assert p.playfulness == 1

def test_social_layer_state_detection():
    assert SocialResponseLayer.detect_state("Hola JARVIS") == ConversationState.CASUAL
    assert SocialResponseLayer.detect_state("Estoy cansado") == ConversationState.EMPATHETIC
    assert SocialResponseLayer.detect_state("Tengo una reunión en 5 minutos") == ConversationState.URGENT
    assert SocialResponseLayer.detect_state("Organízame el día") == ConversationState.PRODUCTIVE
    assert SocialResponseLayer.detect_state("Ponme música") == ConversationState.ENTERTAINMENT
    assert SocialResponseLayer.detect_state("Háblame más corto") == ConversationState.FEEDBACK

def test_natural_variation_phrases():
    p = PersonalityProfile()
    phrase = SocialResponseLayer.format_social_tool_phrase(
        tool_name="open_application",
        tool_args={"app_name": "Chrome"},
        tool_result={"success": True, "data": {}},
        personality=p
    )
    assert "Chrome" in phrase
    assert not phrase.startswith("A su disposición")

@pytest.mark.asyncio
async def test_feedback_handling_in_orchestrator():
    orch = JarvisOrchestrator(primary_provider=MockAIProvider())
    res_short = await orch.process_user_input("Háblame más corto")
    assert res_short["success"] is True
    assert "directo" in res_short["response_text"].lower()

    res_fun = await orch.process_user_input("Háblame más divertido")
    assert res_fun["success"] is True
    assert "chispa" in res_fun["response_text"].lower()

    res_serious = await orch.process_user_input("Deja de hacer bromas")
    assert res_serious["success"] is True
    assert "sobrio" in res_serious["response_text"].lower()

@pytest.mark.asyncio
async def test_casual_and_empathy_prompts():
    orch = JarvisOrchestrator(primary_provider=MockAIProvider())
    
    res_what = await orch.process_user_input("¿Qué haces?")
    assert res_what["success"] is True
    assert "Esperándote" in res_what["response_text"] or "¿Qué" in res_what["response_text"]

    res_tired = await orch.process_user_input("Estoy cansado")
    assert res_tired["success"] is True
    assert "ritmo" in res_tired["response_text"] or "organizar" in res_tired["response_text"]

def test_companion_conversational_system_instruction():
    orch = JarvisOrchestrator(primary_provider=MockAIProvider())
    sys_prompt = orch._build_system_instruction("Cómo estructurar un proyecto")
    assert "COMPAÑERA CONVERSACIONAL" in sys_prompt
    assert "Calidez (70/100)" in sys_prompt
    assert "Humor y espontaneidad (65/100)" in sys_prompt
    assert "Iniciativa conversacional (60/100)" in sys_prompt
    assert "FORMATO MARKDOWN" in sys_prompt
    assert "REVISIÓN INTERNA PREVIA DE NATURALIDAD" in sys_prompt

def test_markdown_frontend_assets_present():
    from fastapi.testclient import TestClient
    from api.server import app
    client = TestClient(app)

    res_html = client.get("/")
    assert "marked.min.js" in res_html.text

    res_js = client.get("/static/script.js")
    assert "formatAssistantMessage" in res_js.text
    assert "renderMarkdownNative" in res_js.text
    assert "marked.parse" in res_js.text

    res_css = client.get("/static/style.css")
    assert ".msg-content ul" in res_css.text
    assert ".msg-content ol" in res_css.text
    assert ".msg-content pre" in res_css.text
    assert ".msg-content blockquote" in res_css.text

