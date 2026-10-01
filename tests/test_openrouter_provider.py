import pytest
import asyncio
from providers.openrouter_provider import OpenRouterProvider

@pytest.mark.asyncio
async def test_openrouter_init_and_conversion():
    provider = OpenRouterProvider(api_key="sk-or-v1-test-fake-key-1234567890")
    assert provider.name == "openrouter"
    assert provider.is_configured() is True
    
    headers = provider._get_headers()
    assert "Authorization" in headers
    assert "Bearer sk-or-v1-test" in headers["Authorization"]
    assert headers["HTTP-Referer"] == "https://github.com/jarvis-assistant"
    assert headers["X-Title"] == "JARVIS AI Assistant"

    # Conversión de mensajes
    msgs = [{"role": "human", "content": "Hola Jarvis"}]
    converted = provider._convert_messages(msgs, system_prompt="Eres un asistente")
    assert len(converted) == 2
    assert converted[0]["role"] == "system"
    assert converted[1]["role"] == "user"

    # Conversión de tools
    tools = [{
        "name": "play_music",
        "description": "Reproduce música",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}}
    }]
    conv_tools = provider._convert_tools(tools)
    assert len(conv_tools) == 1
    assert conv_tools[0]["type"] == "function"
    assert conv_tools[0]["function"]["name"] == "play_music"
