"""
tests/test_image_service.py - Pruebas automatizadas para el servicio de resolución de imágenes reales
y endpoints de tarjetas showcase sin emojis.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from api.server import app
from core.image_service import ImageSearchService

client = TestClient(app)

def test_clean_query_utility():
    assert ImageSearchService.clean_query("### 01. Cacio e Pepe") == "Cacio e Pepe"
    assert ImageSearchService.clean_query("1. **Ossobuco a la Milanesa** (Lombardía)") == "Ossobuco a la Milanesa"
    assert ImageSearchService.clean_query("02 - Gnocchi al Pesto 🧀") == "Gnocchi al Pesto"
    assert ImageSearchService.clean_query("") == ""
    assert ImageSearchService.clean_query("   ") == ""

def test_image_search_cache_mechanism():
    ImageSearchService.clear_cache()
    # Inyectar una respuesta en la caché
    ImageSearchService._cache["pizza margherita"] = (10000000000.0, "https://example.com/pizza.jpg")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    res = loop.run_until_complete(ImageSearchService.search_image("Pizza Margherita"))
    assert res == "https://example.com/pizza.jpg"
    loop.close()

def test_api_images_search_endpoint_with_cache():
    ImageSearchService.clear_cache()
    ImageSearchService._cache["tiramisu"] = (10000000000.0, "https://example.com/tiramisu.jpg")
    
    res = client.get("/api/images/search?q=Tiramisu")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert data["data"]["image_url"] == "https://example.com/tiramisu.jpg"
    assert data["data"]["query"] == "Tiramisu"

def test_api_images_search_empty_query():
    res = client.get("/api/images/search?q=")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert data["data"]["image_url"] is None

def test_ui_no_emojis_in_showcase_and_has_real_image_resolver():
    res_js = client.get("/static/script.js")
    assert res_js.status_code == 200
    js = res_js.text

    # 1. Prohibido tener getThemedFallbackIcon con emojis en el script
    assert "getThemedFallbackIcon" not in js
    assert "showcase-fallback-icon" not in js

    # 2. Obligatorio tener manejador de errores resiliente y resolvedor asíncrono
    assert "window.handleShowcaseImgError" in js
    assert "window.resolveShowcaseCardImages" in js
    assert "/api/images/search?q=" in js
    assert "no-thumb" in js

    # 3. CSS debe soportar estado sin imagen y skeleton loader
    res_css = client.get("/static/style.css")
    assert res_css.status_code == 200
    css = res_css.text
    assert ".jarvis-showcase-card.no-thumb" in css
    assert ".showcase-skeleton-box" in css
    assert "showcase-shimmer-anim" in css
