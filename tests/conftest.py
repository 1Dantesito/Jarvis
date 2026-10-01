import pytest
import sqlite3
from core.config import settings

@pytest.fixture(autouse=True, scope="session")
def clean_db_around_session():
    """Garantiza que antes y tras ejecutar las pruebas, la base de datos quede 100% limpia."""
    def _clean():
        try:
            conn = sqlite3.connect(settings.DB_PATH)
            c = conn.cursor()
            c.execute("DELETE FROM tasks")
            c.execute("DELETE FROM reminders")
            c.execute("DELETE FROM apscheduler_jobs")
            c.execute("DELETE FROM memories WHERE id > 15 OR key LIKE 'test_%' OR key = 'hobby_temporal'")
            conn.commit()
            conn.close()
        except Exception:
            pass

    _clean()
    yield
    _clean()

@pytest.fixture(autouse=True, scope="session")
def suppress_plyer_native_toast():
    """Evita excepciones de hilo en Windows al invocar notificaciones balloon en sesiones headless de testing."""
    try:
        from plyer import notification
        original_notify = notification.notify
        notification.notify = lambda *args, **kwargs: None
        yield
        notification.notify = original_notify
    except Exception:
        yield


@pytest.fixture(autouse=True, scope="session")
def isolate_api_server_offline():
    """Garantiza que el servidor API y TestClient operen 100% offline sin consumir cuota real de Gemini."""
    try:
        import api.server as server_mod
        from providers.mock_provider import MockAIProvider
        
        mock_p = MockAIProvider()
        server_mod.orchestrator.providers = [mock_p]
        server_mod.orchestrator.primary_provider = mock_p
        server_mod.orchestrator.mock_provider = mock_p
        
        async def _mock_health():
            return {
                "version": settings.VERSION,
                "gemini": {"status": "ok", "model": "mock-rules-engine", "latency_ms": 0.5, "error": None},
                "openrouter": {"status": "ok", "model": "mock-rules-engine", "latency_ms": 0.5, "error": None},
                "anthropic": {"status": "ok", "model": "mock-rules-engine", "latency_ms": 0.5, "error": None},
                "youtube": {"status": "ok", "service": "youtube", "error": None},
                "spotify": {"status": "ok", "service": "spotify", "error": None},
                "timestamp": 1234567890.0
            }
        
        server_mod.perform_health_check = _mock_health
    except Exception:
        pass
    yield



