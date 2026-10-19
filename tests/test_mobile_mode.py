import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from api.server import app
from core.network_tunnel import NetworkTunnelManager, tunnel_manager
from core.config import settings

client = TestClient(app)

def test_tunnel_manager_local_ip_and_urls():
    mgr = NetworkTunnelManager()
    local_ip = mgr.get_local_ip()
    assert isinstance(local_ip, str)
    assert len(local_ip) >= 7

    local_url = mgr.get_local_url(5001)
    assert local_url.startswith("http://")
    assert ":5001" in local_url

def test_tunnel_manager_qr_generation():
    mgr = NetworkTunnelManager()
    test_url = "https://jarvis-test.trycloudflare.com"

    terminal_qr = mgr.generate_terminal_qr(test_url)
    assert isinstance(terminal_qr, str)
    assert len(terminal_qr) > 50

    svg_qr = mgr.generate_svg_qr(test_url)
    assert isinstance(svg_qr, str)
    assert "<svg" in svg_qr
    assert "</svg>" in svg_qr

def test_get_mobile_connection_info_structure():
    mgr = NetworkTunnelManager()
    info = mgr.get_mobile_connection_info(port=5001)
    assert "local_url" in info
    assert "recommended_url" in info
    assert "qr_svg" in info
    assert "instructions" in info
    assert info["pwa_ready"] is True
    assert "<svg" in info["qr_svg"]

def test_api_mobile_info_endpoint():
    res = client.get("/api/mobile/info")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert "data" in data
    assert "local_url" in data["data"]
    assert "qr_svg" in data["data"]

def test_api_mobile_tunnel_stop_endpoint():
    res = client.post("/api/mobile/tunnel/stop")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert data["data"]["tunnel_active"] is False

def test_pwa_manifest_and_icons():
    manifest_path = settings.STATIC_DIR / "manifest.json"
    assert manifest_path.exists(), "El archivo manifest.json debe existir en static/"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    assert manifest_data.get("display") == "standalone"
    assert manifest_data.get("name")
    assert len(manifest_data.get("icons", [])) >= 2

    for icon in manifest_data["icons"]:
        icon_path = settings.BASE_DIR / icon["src"].lstrip("/")
        assert icon_path.exists(), f"El icono {icon['src']} debe existir"

def test_service_worker_asset_caching():
    sw_path = settings.STATIC_DIR / "sw.js"
    assert sw_path.exists(), "El archivo sw.js debe existir en static/"
    content = sw_path.read_text(encoding="utf-8")
    assert "addEventListener('install'" in content
    assert "addEventListener('fetch'" in content

def test_index_html_mobile_elements():
    index_path = settings.TEMPLATES_DIR / "index.html"
    assert index_path.exists()
    content = index_path.read_text(encoding="utf-8")

    # Botón y modal de celular
    assert 'id="btn-open-mobile"' in content
    assert 'id="mobile-connect-modal"' in content
    assert 'id="qr-svg-wrapper"' in content
    assert 'id="mobile-active-url"' in content

    # YouTube player transparente para celular y desktop (no display:none ni offscreen throttling)
    assert 'id="ytplayer-container"' in content
    assert 'position:fixed' in content or 'position: fixed' in content
    assert 'pointer-events:none' in content or 'pointer-events: none' in content

def test_css_mobile_modal_and_safe_areas():
    css_path = settings.STATIC_DIR / "style.css"
    assert css_path.exists()
    content = css_path.read_text(encoding="utf-8")

    assert ".mobile-modal" in content
    assert ".qr-display-container" in content
    assert "safe-area-inset-top" in content
    assert "safe-area-inset-bottom" in content

def test_jarvis_apk_exists_and_downloadable():
    apk_file = settings.BASE_DIR / "JARVIS.apk"
    assert apk_file.exists(), "JARVIS.apk debe existir en la raíz del proyecto"
    assert apk_file.stat().st_size > 5_000_000, "JARVIS.apk debe tener un tamaño válido (>5MB)"

    res = client.get("/download/jarvis.apk")
    assert res.status_code == 200
    assert "application/vnd.android.package-archive" in res.headers.get("content-type", "")
    assert len(res.content) > 5_000_000

