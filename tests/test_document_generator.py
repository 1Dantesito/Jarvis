import pytest
from pathlib import Path
from core.document_generator import DocumentGenerator
from core.security import SecurityPolicy
from tools.router import ToolRouter
from tools.implementations.desktop_tools import CreatePdfTool, CreateDocxTool, GenerateImageTool

@pytest.mark.asyncio
async def test_pdf_generation_apa():
    res = DocumentGenerator.create_pdf(
        filename="test_doc_apa.pdf",
        title="Documento de Prueba Científica",
        content="# Introducción\nEste es un párrafo en formato formal APA.\n## Sección 2\n- Punto 1\n- Punto 2",
        author="Dante",
        location="desktop"
    )
    assert res["success"] is True
    assert res["format"] == "PDF"
    path = Path(res["path"])
    assert path.exists()
    assert path.stat().st_size > 500

    # Limpiar archivo de prueba
    try:
        path.unlink()
    except Exception:
        pass

@pytest.mark.asyncio
async def test_docx_generation():
    res = DocumentGenerator.create_docx(
        filename="test_doc_word.docx",
        title="Documento de Prueba Word",
        content="# Título 1\nPárrafo de prueba editable en Microsoft Word.\n- Elemento viñeta",
        author="Dante",
        location="desktop"
    )
    assert res["success"] is True
    assert res["format"] == "DOCX"
    path = Path(res["path"])
    assert path.exists()
    assert path.stat().st_size > 500

    # Limpiar archivo de prueba
    try:
        path.unlink()
    except Exception:
        pass

@pytest.mark.asyncio
async def test_create_pdf_tool_execution():
    router = ToolRouter()
    router.register_tool(CreatePdfTool())

    res = await router.execute_tool("create_pdf", {
        "filename": "test_tool_doc.pdf",
        "title": "Documento Vía Router",
        "content": "Contenido generado a través del ToolRouter.",
        "author": "Dante"
    })
    assert res["success"] is True
    assert "data" in res
    path = Path(res["data"]["path"])
    assert path.exists()

    try:
        path.unlink()
    except Exception:
        pass

@pytest.mark.asyncio
async def test_create_docx_tool_execution():
    router = ToolRouter()
    router.register_tool(CreateDocxTool())

    res = await router.execute_tool("create_docx", {
        "filename": "test_tool_doc.docx",
        "title": "Documento Word Vía Router",
        "content": "Contenido Word generado a través del ToolRouter.",
        "author": "Dante"
    })
    assert res["success"] is True
    assert "data" in res
    path = Path(res["data"]["path"])
    assert path.exists()

    try:
        path.unlink()
    except Exception:
        pass

def test_generate_image_tool_registration():
    router = ToolRouter()
    router.register_tool(GenerateImageTool())
    schemas = router.get_tools_schema_gemini()
    names = [s["name"] for s in schemas]
    assert "generate_image" in names

def test_security_safe_actions_inclusion():
    assert "create_pdf" in SecurityPolicy.SAFE_ACTIONS
    assert "create_docx" in SecurityPolicy.SAFE_ACTIONS
    assert "generate_image" in SecurityPolicy.SAFE_ACTIONS

@pytest.mark.asyncio
async def test_generate_image_tool_mock(monkeypatch):
    from core.image_generator import ImageGenerator
    async def mock_gen(prompt, filename=None, location="pictures", style=None, **kwargs):
        return {
            "success": True,
            "file_name": "test_robot.png",
            "path": "C:\\Users\\mock\\test_robot.png",
            "data_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            "prompt": prompt
        }
    monkeypatch.setattr(ImageGenerator, "generate_image", mock_gen)

    router = ToolRouter()
    router.register_tool(GenerateImageTool())
    res = await router.execute_tool("generate_image", {"prompt": "un robot futurista azul"})
    assert res["success"] is True
    assert res["data"]["file_name"] == "test_robot.png"

@pytest.mark.asyncio
async def test_pdf_with_table():
    content = """# Reporte Financiero
Este documento incluye una tabla comparativa:

| Trimestre | Ingresos | Gastos | Beneficio |
| --- | --- | --- | --- |
| Q1 | $10,000 | $6,000 | $4,000 |
| Q2 | $15,000 | $8,000 | $7,000 |
| Q3 | $20,000 | $9,500 | $10,500 |

Fin del reporte.
"""
    res = DocumentGenerator.create_pdf(
        filename="test_table_doc.pdf",
        title="Reporte con Tablas",
        content=content,
        author="Dante"
    )
    assert res["success"] is True
    p = Path(res["path"])
    assert p.exists()
    assert p.stat().st_size > 1000
    try:
        p.unlink()
    except Exception:
        pass

@pytest.mark.asyncio
async def test_docx_with_table():
    content = """# Reporte Financiero DOCX
| Producto | Unidades | Precio |
| --- | --- | --- |
| Laptop | 5 | $1,200 |
| Monitor | 10 | $300 |
"""
    res = DocumentGenerator.create_docx(
        filename="test_table_doc.docx",
        title="Reporte con Tablas Word",
        content=content,
        author="Dante"
    )
    assert res["success"] is True
    p = Path(res["path"])
    assert p.exists()
    assert p.stat().st_size > 1000
    try:
        p.unlink()
    except Exception:
        pass

@pytest.mark.asyncio
async def test_parse_blocks_with_images_and_html():
    content = """# Documento Científico
Párrafo inicial con información previa.
![Planeta Marte]("marte.png")
Texto intermedio.
<img src="jupiter.png" alt="Planeta Júpiter" />
Párrafo final."""
    blocks = DocumentGenerator._parse_blocks(content)
    types = [b["type"] for b in blocks]
    assert "h1" in types
    assert "image" in types
    images = [b for b in blocks if b["type"] == "image"]
    assert len(images) == 2
    assert images[0]["alt"] == "Planeta Marte"
    assert images[0]["src"] == "marte.png"
    assert images[1]["alt"] == "Planeta Júpiter"
    assert images[1]["src"] == "jupiter.png"

@pytest.mark.asyncio
async def test_pdf_with_image(tmp_path):
    from PIL import Image as PILImage
    test_img = tmp_path / "test_figura.png"
    im = PILImage.new("RGB", (200, 200), color="blue")
    im.save(test_img)

    content = f"""# Estudio Astronómico
A continuación se presenta la imagen captada:

![Telescopio Espacial]({test_img.as_posix()})

Conclusiones del estudio."""

    res = DocumentGenerator.create_pdf(
        filename="test_pdf_con_imagen.pdf",
        title="Estudio con Figuras",
        content=content,
        author="Dante"
    )
    assert res["success"] is True
    p = Path(res["path"])
    assert p.exists()
    assert p.stat().st_size > 1000
    try:
        p.unlink()
    except Exception:
        pass

@pytest.mark.asyncio
async def test_docx_with_image(tmp_path):
    from PIL import Image as PILImage
    test_img = tmp_path / "test_word_figura.png"
    im = PILImage.new("RGB", (150, 150), color="green")
    im.save(test_img)

    content = f"""# Ensayo Visual
![Gráfico Experimental]({test_img.as_posix()})"""

    res = DocumentGenerator.create_docx(
        filename="test_docx_con_imagen.docx",
        title="Ensayo con Imagen",
        content=content,
        author="Dante"
    )
    assert res["success"] is True
    p = Path(res["path"])
    assert p.exists()
    assert p.stat().st_size > 1000
    try:
        p.unlink()
    except Exception:
        pass

def test_resolve_image_base64():
    b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    resolved = DocumentGenerator._resolve_image_file(b64, alt_text="Píxel de prueba")
    assert resolved is not None
    assert resolved.exists()
    assert resolved.suffix == ".png"
    try:
        resolved.unlink()
    except Exception:
        pass

@pytest.mark.asyncio
async def test_orchestrator_safeguard_pdf_with_image(tmp_path):
    from core.orchestrator import JarvisOrchestrator
    from providers.mock_provider import MockAIProvider
    from PIL import Image as PILImage

    im_file = tmp_path / "tubo_vacio.png"
    im = PILImage.new("RGB", (100, 100), color="blue")
    im.save(im_file)

    orch = JarvisOrchestrator(primary_provider=MockAIProvider())
    fake_executed_tools = [{"tool_name": "generate_image", "result": {"success": True, "data": {"path": str(im_file), "prompt": "Tubos de vacío"}}, "spoken_phrase": "Imagen generada."}]
    res = await orch._auto_generate_pdf_with_image_if_requested(
        clean_prompt="quiero que hagas un pdf de los tubos de vacio y agregues referencias visuales",
        executed_tools=[],
        image_result=fake_executed_tools[0]["result"]
    )
    assert res is not None
    assert res["success"] is True
    assert "pdf" in res["data"]["file_name"].lower()
    p = Path(res["data"]["path"])
    assert p.exists()
    assert p.stat().st_size > 1000
    try:
        p.unlink()
    except Exception:
        pass




