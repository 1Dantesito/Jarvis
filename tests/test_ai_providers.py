import pytest
from unittest.mock import AsyncMock, MagicMock
from core.ai_provider import AIProvider
from providers.mock_provider import MockAIProvider
from providers.gemini_provider import GeminiProvider
from providers.anthropic_provider import AnthropicProvider

@pytest.mark.asyncio
async def test_mock_provider():
    mock = MockAIProvider()
    res = await mock.generate_response([{"role": "user", "content": "¿Qué hora es?"}])
    assert res["success"] is True
    assert len(res["tool_calls"]) > 0
    assert res["tool_calls"][0]["name"] == "get_current_datetime"

@pytest.mark.asyncio
async def test_gemini_provider_init(monkeypatch):
    monkeypatch.setattr("core.config.settings.GEMINI_API_KEY", "")
    gemini = GeminiProvider(api_key="")
    assert gemini.name == "gemini"
    assert gemini.client_ready is False

@pytest.mark.asyncio
async def test_anthropic_provider_init(monkeypatch):
    monkeypatch.setattr("core.config.settings.ANTHROPIC_API_KEY", "")
    anthropic = AnthropicProvider(api_key="")
    assert anthropic.name == "anthropic"

@pytest.mark.asyncio
async def test_gemini_provider_contents_and_config():
    gemini = GeminiProvider(api_key="test_dummy_key_no_network")
    contents = gemini._build_contents([
        {"role": "user", "content": "Hola Jarvis"},
        {"role": "assistant", "content": "¿En qué puedo ayudarte?"}
    ])
    assert len(contents) == 2
    assert contents[0].role == "user"
    assert contents[1].role == "model"

    tools = [{
        "name": "get_weather",
        "description": "Get current weather",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"]
        }
    }]
    config = gemini._build_config(system_prompt="Eres un asistente", tools=tools, temperature=0.5)
    assert config is not None
    assert config.temperature == 0.5
    assert config.system_instruction == "Eres un asistente"
    assert len(config.tools) == 1

@pytest.mark.asyncio
async def test_gemini_provider_unconfigured_handling():
    gemini = GeminiProvider(api_key="")
    res = await gemini.generate_response([{"role": "user", "content": "Hola"}])
    assert res["success"] is False
    assert "no configurada" in res["error"]

    hc = await gemini.health_check()
    assert hc["status"] == "not_configured"

@pytest.mark.asyncio
async def test_gemini_provider_mocked_generate_response():
    """Verifica generate_response con mock asíncrono sin llamadas reales a la API."""
    gemini = GeminiProvider(api_key="dummy_key_mock")
    gemini.client_ready = True

    mock_part_text = MagicMock()
    mock_part_text.text = "Respuesta mockeada de Gemini"
    mock_part_text.function_call = None

    mock_candidate = MagicMock()
    mock_candidate.content.parts = [mock_part_text]

    mock_response = MagicMock()
    mock_response.candidates = [mock_candidate]

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
    gemini.client = mock_client

    res = await gemini.generate_response([{"role": "user", "content": "Hola"}])
    assert res["success"] is True
    assert res["text"] == "Respuesta mockeada de Gemini"
    assert mock_client.aio.models.generate_content.called

@pytest.mark.asyncio
async def test_gemini_provider_mocked_tool_call():
    """Verifica llamadas a funciones con mock asíncrono sin consumo de cuota."""
    gemini = GeminiProvider(api_key="dummy_key_mock")
    gemini.client_ready = True

    mock_fc = MagicMock()
    mock_fc.name = "get_current_datetime"
    mock_fc.args = {}

    mock_part_fc = MagicMock()
    mock_part_fc.text = None
    mock_part_fc.function_call = mock_fc

    mock_candidate = MagicMock()
    mock_candidate.content.parts = [mock_part_fc]

    mock_response = MagicMock()
    mock_response.candidates = [mock_candidate]

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
    gemini.client = mock_client

    res = await gemini.generate_response([{"role": "user", "content": "¿Qué hora es?"}])
    assert res["success"] is True
    assert len(res["tool_calls"]) == 1
    assert res["tool_calls"][0]["name"] == "get_current_datetime"
