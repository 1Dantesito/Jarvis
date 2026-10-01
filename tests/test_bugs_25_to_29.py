import pytest
from datetime import datetime, timedelta
from core.time_parser import TimeParser
from core.memory_manager import memory_manager
from core.social_layer import SocialResponseLayer
from core.user_profile import PersonalityProfile
from core.notification_engine import NotificationEngine
from tools.router import TOOL_REGISTRY, ToolType

def test_bug27_time_parser_pm_and_colloquial_resolution():
    """BUG-27: Verifica que frases completas, números directos y expresiones coloquiales se interpreten exactamente."""
    # 1. Caso exacto reportado con frase larga
    p1 = TimeParser.parse("generar un nuevo recordatorio para las 7:50 p.m. del día de hoy")
    assert p1["success"] is True
    assert p1["time_24h"] == "19:50"
    assert "7:50 PM" in p1["time_12h"]
    assert "PM" in p1["datetime_formatted"]

    # 2. Número directo '750 p.m'
    p2 = TimeParser.parse("750 p.m")
    assert p2["success"] is True
    assert p2["time_24h"] == "19:50"
    assert p2["time_12h"] == "7:50 PM"

    # 3. Coloquial 'a las 7 y 50 pm'
    p3 = TimeParser.parse("a las 7 y 50 pm")
    assert p3["success"] is True
    assert p3["time_24h"] == "19:50"

    # 4. '7 y media de la noche'
    p4 = TimeParser.parse("a las 7 y media de la noche")
    assert p4["success"] is True
    assert p4["time_24h"] == "19:30"

    # 5. '8 en punto'
    p5 = TimeParser.parse("8 en punto")
    assert p5["success"] is True
    assert p5["time_24h"] in ["20:00", "08:00"]

    # 6. 'avísame mañana a las 9 am por favor'
    p6 = TimeParser.parse("avísame mañana a las 9 am por favor")
    assert p6["success"] is True
    assert p6["time_24h"] == "09:00"
    assert p6["time_12h"] == "9:00 AM"

def test_bug26_composite_deduplication():
    """BUG-26: Verifica deduplicación compuesta (mismo título y misma hora vs distinta hora)."""
    # Mismo título pero distinta hora -> Deben ser dos recordatorios distintos
    r1 = memory_manager.create_reminder("Tomar agua diaria", "a las 3:00 pm")
    r2 = memory_manager.create_reminder("Tomar agua diaria", "a las 8:00 pm")
    assert r1["success"] is True
    assert r2["success"] is True
    assert r1["data"]["id"] != r2["data"]["id"]

    # Mismo título y misma hora -> Deduplicación exacta
    r3 = memory_manager.create_reminder("Tomar agua diaria", "a las 3:00 pm")
    assert r3["success"] is True
    assert r3["data"]["id"] == r1["data"]["id"]

def test_bug31_notification_engine_trigger_and_broadcast():
    """BUG-31: Verifica que recordatorios vencidos disparen notificaciones y broadcast callbacks."""
    received_alarms = []
    def dummy_ws_cb(alarm):
        received_alarms.append(alarm)

    NotificationEngine.register_broadcast_callback(dummy_ws_cb)

    # Crear recordatorio vencido (1 minuto en el pasado)
    past_time = (datetime.now().astimezone() - timedelta(minutes=1)).isoformat()
    r = memory_manager.create_reminder("Recordatorio de prueba alarma", "en 1 minuto")
    
    # Forzar target datetime en el pasado en la base de datos para simular vencimiento
    from core.database import SessionLocal, ReminderModel
    db = SessionLocal()
    rem = db.query(ReminderModel).filter(ReminderModel.id == r["data"]["id"]).first()
    rem.target_datetime_iso = past_time
    db.commit()
    db.close()

    # Ejecutar evaluación de recordatorios
    dispatched = NotificationEngine.check_and_notify_due_reminders()
    assert any(d["reminder_id"] == r["data"]["id"] for d in dispatched)
    assert any(a["reminder_id"] == r["data"]["id"] for a in received_alarms)

def test_bug32_clean_profile_memory():
    """BUG-32: Verifica que el nombre del usuario no contenga datos de prueba como 'Dante Test'."""
    profile = memory_manager.get_all_profile()
    name = profile.get("full_name") or profile.get("name", "")
    assert "Test" not in name
    assert "Jhonatan" in name
