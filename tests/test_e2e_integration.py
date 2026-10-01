import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import asyncio
from core.orchestrator import JarvisOrchestrator
from core.memory_manager import memory_manager, MemoryType
from core.music_engine import music_engine, PlaybackState
from core.notification_engine import NotificationEngine, ReminderScheduler
from core.windows_automation import WindowsAutomationProvider
from core.voice_state_machine import VoiceStateMachine, VoiceState
from core.security import SecurityPolicy, ActionRisk
from providers.mock_provider import MockAIProvider

@pytest.mark.asyncio
async def test_e2e_voice_and_bargein_lifecycle():
    vsm = VoiceStateMachine()
    assert vsm.current_state == VoiceState.IDLE

    # Transición a LISTENING
    assert vsm.transition_to(VoiceState.LISTENING) is True
    gen_id_1 = vsm.current_generation_id

    # Transición a PROCESSING y SPEAKING
    assert vsm.transition_to(VoiceState.PROCESSING) is True
    assert vsm.transition_to(VoiceState.SPEAKING) is True

    # Barge-in: interrupción inmediata
    assert vsm.trigger_barge_in() is True
    assert vsm.current_state == VoiceState.LISTENING
    assert vsm.current_generation_id > gen_id_1

@pytest.mark.asyncio
async def test_e2e_memory_persistence_and_recall_cycle():
    # 1. Guardar memoria explícita
    res_store = memory_manager.store_memory(
        key="preferencia_comunicacion",
        value="Respuestas directas y concisas",
        mem_type=MemoryType.SYSTEM_PREFERENCE
    )
    assert res_store["success"] is True

    # 2. Consultar mediante orquestador
    orch = JarvisOrchestrator(primary_provider=MockAIProvider())
    res_query = await orch.process_user_input("¿Qué recuerdas de mí?")
    assert res_query["success"] is True

    # 3. Olvidar memoria
    res_forget = memory_manager.forget_memory("preferencia_comunicacion")
    assert res_forget["success"] is True
    assert res_forget["forgotten_count"] >= 1

@pytest.mark.asyncio
async def test_e2e_reminders_and_scheduler_lifecycle():
    # 1. Crear recordatorio
    res = memory_manager.create_reminder(
        title="Probar QA Integral Fase 12",
        remind_at_expression="en 5 minutos",
        priority="HIGH"
    )
    assert res["success"] is True
    rem_id = res["data"]["id"]

    # 2. Pospuesto (Snooze)
    res_snooze = memory_manager.snooze_reminder(rem_id, minutes=15)
    assert res_snooze["success"] is True
    assert res_snooze["data"]["status"] == "SNOOZED"

    # 3. Completado
    success = memory_manager.complete_reminder(rem_id)
    assert success is True

@pytest.mark.asyncio
async def test_e2e_multimedia_smart_queue_continuous_playback(monkeypatch):
    from unittest.mock import AsyncMock
    from core.media_provider import TrackItem
    from core.youtube_provider import YouTubeProvider
    mock_tracks = [
        TrackItem(id="vid_lp_1", title="In the End", artist="Linkin Park"),
        TrackItem(id="vid_lp_2", title="Numb", artist="Linkin Park"),
        TrackItem(id="vid_lp_3", title="Faint", artist="Linkin Park")
    ]
    monkeypatch.setattr(YouTubeProvider, "search_tracks", AsyncMock(return_value=mock_tracks))

    # 1. Iniciar reproducción continua
    res = await music_engine.play_query("Linkin Park")
    assert res["success"] is True
    assert res["status"] == "PLAYBACK_STARTED"
    assert len(res["playlist"]) > 0

    # 2. Pausa y Reanudar
    p = music_engine.pause()
    assert p["status"] == "PAUSED"
    r = music_engine.resume()
    assert r["status"] == "PLAYING"

    # 3. Skip con auto-relleno de SmartQueue
    s = await music_engine.skip()
    assert s["success"] is True

    # 4. Estado Now Playing
    np = music_engine.get_now_playing()
    assert np["is_playing"] is True
    assert "linkin park" in np["summary"].lower()

    # 5. Limpieza
    cl = music_engine.clear_queue()
    assert cl["success"] is True

@pytest.mark.asyncio
async def test_e2e_security_sandbox_and_critical_protection():
    # 1. Comandos destructivos bloqueados
    assert SecurityPolicy.is_dangerous("del /f /s C:/Windows") is True
    assert SecurityPolicy.is_dangerous("rmdir /s /q System32") is True
    assert SecurityPolicy.is_dangerous("echo Seguro") is False

    # 2. Protección de procesos críticos
    res_close = WindowsAutomationProvider.close_application("explorer.exe")
    assert res_close["success"] is False
    assert res_close["status"] in ["BLOCKED_CRITICAL_PROCESS", "APP_NOT_ALLOWED"]

    # 3. Acción destructiva requiere confirmación en el orquestador
    orch = JarvisOrchestrator(primary_provider=MockAIProvider())
    res_destruct = await orch.process_user_input("Elimina esta carpeta")
    assert res_destruct["action_type"] == "security_confirmation"
