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

@pytest.mark.asyncio
async def test_create_reminder_tool_flexible_aliases():
    from tools.implementations.reminder_tools import CreateReminderTool
    from core.memory_manager import memory_manager
    tool = CreateReminderTool()
    
    # 1. Llamada usando 'time' en vez de 'remind_at' y 'task' en vez de 'title'
    res1 = await tool.execute(task="Tomar vitaminas", time="a las 5:00 pm", priority="HIGH")
    assert res1["success"] is True
    assert res1["data"]["title"] == "Tomar vitaminas"
    assert "5:00 PM" in res1["data"]["display_datetime"] or "17:00" in res1["data"]["target_datetime_iso"]
    
    # 2. Llamada usando 'when' y 'reminder'
    res2 = await tool.execute(reminder="Reunión cliente", when="mañana a las 10 am")
    assert res2["success"] is True
    assert res2["data"]["title"] == "Reunión cliente"

def test_calendar_date_persistence_and_exact_time():
    from core.memory_manager import memory_manager
    from core.database import SessionLocal, ReminderModel
    
    # 1. Fechas con nombre de mes en español
    res = memory_manager.create_reminder(
        title="Entrega de proyecto",
        remind_at_expression="5 de octubre a las 4 pm",
        priority="URGENT"
    )
    assert res["success"] is True
    rem_id = res["data"]["id"]
    
    db = SessionLocal()
    rem = db.query(ReminderModel).filter(ReminderModel.id == rem_id).first()
    assert rem is not None
    assert "-10-05T16:00:00" in rem.target_datetime_iso
    assert "5 de octubre" in rem.display_datetime
    assert "4:00 PM" in rem.display_datetime
    db.close()

def test_rollover_when_hour_already_passed():
    from core.time_parser import TimeParser
    # Si la referencia es a las 6:00 PM y se pide "a las 10:00 am" sin fecha
    ref_late = datetime(2026, 10, 1, 18, 0).astimezone()
    res = TimeParser.parse("a las 10:00 am", reference_dt=ref_late)
    assert res["success"] is True
    # Debe programarse para el día siguiente (2 de octubre)
    assert "2026-10-02" in res["datetime_iso"]
    assert res["time_24h"] == "10:00"

def test_recurrent_reminder_creation_and_recurrence_advance():
    from core.memory_manager import memory_manager
    from core.notification_engine import NotificationEngine
    from core.database import SessionLocal, ReminderModel

    # Crear recordatorio recurrente "cada día a las 8 am"
    res = memory_manager.create_reminder(
        title="Rutina matutina",
        remind_at_expression="todos los días a las 8 am"
    )
    assert res["success"] is True
    assert res["data"]["is_recurring"] is True
    rem_id = res["data"]["id"]

    db = SessionLocal()
    rem = db.query(ReminderModel).filter(ReminderModel.id == rem_id).first()
    assert rem.is_recurring is True
    assert rem.recurrence_rule is not None
    
    # Simular que venció hace 1 segundo y evaluar NotificationEngine
    target_dt = datetime.fromisoformat(rem.target_datetime_iso)
    simulated_now = target_dt + timedelta(seconds=2)
    notifications = NotificationEngine.check_and_notify_due_reminders(reference_now=simulated_now)
    assert any(n["reminder_id"] == rem_id for n in notifications)

    # El recordatorio recurrente debe mantenerse en PENDING y avanzar al día siguiente
    db.refresh(rem)
    assert rem.status == "PENDING"
    new_target = datetime.fromisoformat(rem.target_datetime_iso)
    assert new_target > target_dt
    db.close()

def test_reminder_rest_api_endpoints():
    from fastapi.testclient import TestClient
    from api.server import app
    client = TestClient(app)

    # 1. POST /api/reminders
    create_res = client.post("/api/reminders", json={
        "title": "Prueba API REST",
        "remind_at": "en 45 minutos",
        "priority": "HIGH"
    })
    assert create_res.status_code == 200
    json_data = create_res.json()
    assert json_data["ok"] is True
    rem_id = json_data["data"]["id"]

    # 2. GET /api/reminders
    get_res = client.get("/api/reminders")
    assert get_res.status_code == 200
    assert any(r["id"] == rem_id for r in get_res.json()["data"])

    # 3. POST /api/reminders/{id}/snooze
    snooze_res = client.post(f"/api/reminders/{rem_id}/snooze", json={"minutes": 15})
    assert snooze_res.status_code == 200
    assert snooze_res.json()["ok"] is True
    assert snooze_res.json()["data"]["status"] == "SNOOZED"

    # 4. POST /api/reminders/{id}/complete
    comp_res = client.post(f"/api/reminders/{rem_id}/complete")
    assert comp_res.status_code == 200
    assert comp_res.json()["ok"] is True

    # 5. DELETE /api/reminders/{id}
    del_res = client.delete(f"/api/reminders/{rem_id}")
    assert del_res.status_code == 200
    assert del_res.json()["ok"] is True

