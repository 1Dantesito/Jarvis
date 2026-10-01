import pytest
from datetime import datetime, timedelta
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

from core.reminders import reminder_engine, send_native_notification
from core.database import SessionLocal, ReminderModel, init_db

@pytest.fixture(scope="module", autouse=True)
def setup_teardown():
    init_db()
    reminder_engine.start()
    yield
    reminder_engine.stop()

def test_parse_recurrent_weekly():
    trigger, is_rec, dt, desc = reminder_engine.parse_time_expression("cada lunes a las 9am")
    assert is_rec is True
    assert isinstance(trigger, CronTrigger)
    assert "Lunes" in desc or "lunes" in desc
    assert "09:00" in desc

def test_parse_recurrent_daily():
    trigger, is_rec, dt, desc = reminder_engine.parse_time_expression("todos los días a las 8am")
    assert is_rec is True
    assert isinstance(trigger, CronTrigger)
    assert "08:00" in desc

def test_parse_recurrent_interval():
    trigger, is_rec, dt, desc = reminder_engine.parse_time_expression("cada 30 minutos")
    assert is_rec is True
    assert isinstance(trigger, IntervalTrigger)
    assert "30 minutos" in desc

def test_parse_punctual_dateparser():
    trigger, is_rec, dt, desc = reminder_engine.parse_time_expression("en 20 minutos")
    assert is_rec is False
    assert isinstance(trigger, DateTrigger)
    assert dt is not None
    now = datetime.now().astimezone()
    # Debe estar aproximadamente 20 minutos en el futuro (19 - 21 min)
    diff = (dt - now).total_seconds() / 60
    assert 18 <= diff <= 22

def test_schedule_and_persistence_sqlite():
    # Programar recordatorio puntual
    res = reminder_engine.schedule_reminder(
        title="Revisar despliegue",
        time_expression="en 15 minutos",
        priority="HIGH"
    )
    assert res["success"] is True
    rem_id = res["data"]["id"]

    # Verificar que existe en la tabla de recordatorios de SQLite
    db = SessionLocal()
    rem = db.query(ReminderModel).filter(ReminderModel.id == rem_id).first()
    assert rem is not None
    assert rem.title == "Revisar despliegue"
    assert rem.priority == "HIGH"
    assert rem.status == "PENDING"
    db.close()

    # Simular reinicio del planificador
    reminder_engine.stop()
    reminder_engine.start()

    # Verificar que el job sigue cargado en el scheduler tras reiniciar
    job = reminder_engine._scheduler.get_job(f"jarvis_reminder_{rem_id}")
    assert job is not None

    # Limpiar cancelando
    ok = reminder_engine.cancel_reminder(rem_id)
    assert ok is True

def test_native_notification_dispatch():
    # Prueba que la función de notificación nativa se ejecuta sin lanzar excepción
    success = send_native_notification(
        title="Prueba Unitaria",
        message="Validando notificación independiente de la web",
        priority="NORMAL"
    )
    assert success is True
