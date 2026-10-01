import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from tools.implementations.web_tools import ReadWebpageTool, WebSearchTool, extract_clean_text_from_html
from tools.router import ToolRouter, ToolType

def test_extract_clean_text_from_html():
    raw_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Documentación de Prueba - JARVIS</title>
        <style>body { font-family: sans-serif; } .nav { display: none; }</style>
        <script>console.log("analytics tracking code");</script>
    </head>
    <body>
        <nav><a href="/">Inicio</a></nav>
        <header><h1>Encabezado Omitido</h1></header>
        <main>
            <h2>Introducción a la IA</h2>
            <p>La inteligencia artificial es un campo de la computación que <b>transforma</b> el mundo.</p>
            <p>JARVIS v4.0 integra <i>lectura web profunda</i> y caché local.</p>
        </main>
        <footer><p>Copyright 2026. Todos los derechos reservados.</p></footer>
    </body>
    </html>
    """
    title, text = extract_clean_text_from_html(raw_html, max_chars=500)
    assert title == "Documentación de Prueba - JARVIS"
    assert "analytics tracking code" not in text
    assert "body { font-family" not in text
    assert "Copyright 2026" not in text
    assert "Inteligencia artificial" in text or "inteligencia artificial" in text
    assert "lectura web profunda" in text

@pytest.mark.asyncio
async def test_read_webpage_execution_and_caching():
    ReadWebpageTool.clear_cache()
    tool = ReadWebpageTool()

    fake_html = """
    <html>
        <head><title>Artículo Especial</title></head>
        <body>
            <p>Contenido principal del artículo para síntesis.</p>
        </body>
    </html>
    """

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = fake_html

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        # 1. Primera lectura (sin caché)
        res1 = await tool.execute(url="https://ejemplo.com/articulo")
        assert res1["success"] is True
        assert res1["data"]["title"] == "Artículo Especial"
        assert "Contenido principal" in res1["data"]["content"]
        assert res1["data"]["cached"] is False
        assert mock_get.call_count == 1

        # 2. Segunda lectura (debe retornar de caché sin llamar de nuevo a HTTP)
        res2 = await tool.execute(url="https://ejemplo.com/articulo")
        assert res2["success"] is True
        assert res2["data"]["cached"] is True
        assert mock_get.call_count == 1  # No aumentó porque usó caché

@pytest.mark.asyncio
async def test_read_webpage_invalid_url():
    tool = ReadWebpageTool()
    res_bad = await tool.execute(url="javascript:alert(1)")
    assert res_bad["success"] is False
    assert "insegura" in res_bad["error"].lower() or "inválida" in res_bad["error"].lower()

def test_web_tools_classification():
    router = ToolRouter()
    assert router.get_tool_type("read_webpage") == ToolType.QUERY
    assert router.get_tool_type("web_search") == ToolType.ACTION
