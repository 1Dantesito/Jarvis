import pytest
from fastapi.testclient import TestClient
from api.server import app, orchestrator
from providers.mock_provider import MockAIProvider

mock_p = MockAIProvider()
orchestrator.providers = [mock_p]
orchestrator.primary_provider = mock_p
orchestrator.mock_provider = mock_p

client = TestClient(app)

def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]

def test_api_chat_empty():
    res = client.post("/api/chat", json={"prompt": ""})
    assert res.status_code == 400
    assert res.json()["ok"] is False

def test_api_chat_message():
    res = client.post("/api/chat", json={"prompt": "ping"})
    assert res.status_code == 200
    body = res.json()
    assert body["ok"] is True
    data = body["data"]
    assert "text" in data
    assert len(data["text"]) > 0

def test_api_profile():
    res = client.get("/api/profile")
    assert res.status_code == 200
    body = res.json()
    assert body["ok"] is True
    assert isinstance(body["data"], dict)

def test_api_reset():
    res = client.post("/api/reset")
    assert res.status_code == 200
    body = res.json()
    assert body["ok"] is True
    assert body["data"]["status"] == "ok"

def test_api_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    body = res.json()
    assert body["ok"] is True
    data = body["data"]
    assert "version" in data
    assert "openrouter" in data
    assert "gemini" in data
    assert "youtube" in data

def test_session_isolation():
    # Sesión A
    res_a = client.post("/api/chat", json={"prompt": "Mi color favorito es el azul oscuro", "session_id": "session_a"})
    assert res_a.status_code == 200
    assert res_a.json()["ok"] is True
    
    # Sesión B
    res_b = client.post("/api/chat", json={"prompt": "¿Qué color te dije?", "session_id": "session_b"})
    assert res_b.status_code == 200
    assert res_b.json()["ok"] is True
    # En sesión B no debería asumir el contexto de sesión A

def test_sse_chat_streaming():
    res = client.get("/api/chat/stream?prompt=Hola")
    assert res.status_code == 200
    assert "text/event-stream" in res.headers["content-type"]
    content = res.text
    assert "event: " in content or "data: " in content

def test_session_persistence_by_device_id():
    # Primer mensaje con un device_id
    res1 = client.post("/api/chat", json={"prompt": "Mi apodo es Neo", "device_id": "phone_device_123"})
    assert res1.status_code == 200
    body1 = res1.json()
    assert body1["ok"] is True
    sid = body1["data"]["session_id"]
    
    # Segundo mensaje omitiendo session_id pero con el mismo device_id: debe recuperar la sesión
    res2 = client.post("/api/chat", json={"prompt": "¿Cual es mi apodo?", "device_id": "phone_device_123"})
    assert res2.status_code == 200
    body2 = res2.json()
    assert body2["ok"] is True
    assert body2["data"]["session_id"] == sid

def test_websocket_reconnection_preserves_session():
    # Primera conexión WebSocket
    with client.websocket_connect("/ws/v1/chat?session_id=recon_session_1") as ws1:
        sync1 = ws1.receive_json()
        assert sync1["type"] == "sync_state"
        assert sync1["session_id"] == "recon_session_1"
        ws1.send_json({"type": "ping"})
        pong = ws1.receive_json()
        assert pong["type"] == "pong"
        assert pong["session_id"] == "recon_session_1"
    
    # Reconexión con el mismo session_id después de desconectarse: el servidor debe aceptarlo y preservar la sesión
    with client.websocket_connect("/ws/v1/chat?session_id=recon_session_1") as ws2:
        sync2 = ws2.receive_json()
        assert sync2["type"] == "sync_state"
        assert sync2["session_id"] == "recon_session_1"


def test_websocket_user_text_streaming():
    with client.websocket_connect("/ws/v1/chat?session_id=ws_stream_test") as ws:
        sync = ws.receive_json()
        assert sync["type"] == "sync_state"
        ws.send_json({"type": "user_text", "text": "haz una lista de comida italiana"})
        received_types = []
        for _ in range(15):
            msg = ws.receive_json()
            m_type = msg.get("type")
            received_types.append(m_type)
            if m_type == "response_end":
                assert "full_text" in msg
                assert msg["full_text"] != ""
                break
        assert "response_end" in received_types
        assert "error" not in received_types





def test_api_tasks_crud_and_filtering():
    # 1. Crear tarea en lista personalizada
    res1 = client.post("/api/tasks", json={"title": "Comprar pasta", "project": "Supermercado"})
    assert res1.status_code == 200
    b1 = res1.json()
    assert b1["ok"] is True
    t_id = b1["data"]["id"]

    # 2. Listar tareas filtradas por proyecto
    res2 = client.get("/api/tasks?project=Supermercado")
    assert res2.status_code == 200
    b2 = res2.json()
    assert b2["ok"] is True
    tasks = b2["data"]["tasks"]
    assert any(t["id"] == t_id for t in tasks)

    # 3. Completar tarea
    res3 = client.post(f"/api/tasks/{t_id}/complete")
    assert res3.status_code == 200
    assert res3.json()["ok"] is True

    # 4. Vaciar lista
    res4 = client.delete("/api/tasks?project=Supermercado")
    assert res4.status_code == 200
    assert res4.json()["ok"] is True
