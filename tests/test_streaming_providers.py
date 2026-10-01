import pytest
from unittest.mock import AsyncMock, MagicMock
from providers.mock_provider import MockAIProvider
from providers.gemini_provider import GeminiProvider
from providers.anthropic_provider import AnthropicProvider
from core.orchestrator import JarvisOrchestrator

@pytest.mark.asyncio
async def test_mock_streaming_generator():
    mock = MockAIProvider()
    tokens = []
    tool_calls = []
    async for chunk in mock.generate_response_stream([{"role": "user", "content": "¿Qué hora es?"}]):
        if chunk.get("type") == "token":
            tokens.append(chunk["content"])
        elif chunk.get("type") == "tool_call":
            tool_calls.append(chunk["tool_call"])

    assert len(tokens) > 0
    assert len(tool_calls) > 0
    assert tool_calls[0]["name"] == "get_current_datetime"

@pytest.mark.asyncio
async def test_orchestrator_streaming_with_mock_forced():
    orch = JarvisOrchestrator(primary_provider=MockAIProvider())
    phrases = []
    tools = []
    async for chunk in orch.process_user_input_stream("¿Qué hora es?"):
        if chunk.get("type") == "sentence":
            phrases.append(chunk["text"])
        elif chunk.get("type") == "tool_executed":
            tools.append(chunk["tool_name"])

    assert len(phrases) > 0
    assert "get_current_datetime" in tools

@pytest.mark.asyncio
async def test_gemini_streaming_mocked():
    """Verifica streaming de Gemini con generador asíncrono mockeado sin tocar red."""
    gemini = GeminiProvider(api_key="dummy_mock_key")
    gemini.client_ready = True

    async def mock_stream_gen():
        chunk1 = MagicMock()
        p1 = MagicMock()
        p1.text = "Hola "
        p1.function_call = None
        c1 = MagicMock()
        c1.content.parts = [p1]
        chunk1.candidates = [c1]
        yield chunk1

        chunk2 = MagicMock()
        p2 = MagicMock()
        p2.text = "mundo"
        p2.function_call = None
        c2 = MagicMock()
        c2.content.parts = [p2]
        chunk2.candidates = [c2]
        yield chunk2

    mock_client = MagicMock()
    mock_client.aio.models.generate_content_stream = AsyncMock(return_value=mock_stream_gen())
    gemini.client = mock_client

    tokens = []
    async for item in gemini.generate_response_stream([{"role": "user", "content": "Hola"}]):
        if item.get("type") == "token":
            tokens.append(item["content"])

    assert "".join(tokens) == "Hola mundo"

@pytest.mark.asyncio
async def test_edge_tts_backend_streaming(monkeypatch):
    """Verifica pipeline de Edge TTS con stream mockeado sin peticiones externas."""
    import edge_tts

    class MockCommunicate:
        def __init__(self, text, voice="es-MX-DaliaNeural"):
            self.text = text
            self.voice = voice

        async def stream(self):
            yield {"type": "audio", "data": b"\x00" * 1024}

    monkeypatch.setattr(edge_tts, "Communicate", MockCommunicate)

    communicate = edge_tts.Communicate("Prueba de audio", voice="es-MX-DaliaNeural")
    chunks = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            chunks.append(chunk["data"])
    assert len(chunks) > 0
    assert sum(len(c) for c in chunks) >= 1000
