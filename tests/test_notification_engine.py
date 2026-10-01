import pytest
from datetime import datetime, timezone, timedelta
from core.database import SessionLocal, ReminderModel, init_db
from core.notification_engine import NotificationEngine
from core.memory_manager import memory_manager

def setup_module():
    init_db()

def test_toast_dispatch():
    ok = NotificationEngine.send_native_toast("Prueba de Test", "Verificando notificación", priority="LOW")
    assert ok is True

def test_due_reminder_exact_trigger():
    # Crear recordatorio que vence ahora mismo
    now = datetime.now().astimezone()
    res = memory_manager.create_reminder(
        title="Tomar agua",
        remind_at_expression="en 0 minutos",
        priority="NORMAL"
    )
    assert res["success"] is True
    rem_id = res["data"]["id"]

    # Ejecutar ciclo del NotificationEngine
    notifications = NotificationEngine.check_and_notify_due_reminders(reference_now=now)
    assert any(n["reminder_id"] == rem_id and n["stage"] == "exact" for n in notifications)

    # Verificar que no se repita en una segunda ejecución (deduplicación)
    notifications_repeat = NotificationEngine.check_and_notify_due_reminders(reference_now=now)
    assert not any(n["reminder_id"] == rem_id for n in notifications_repeat)

def test_urgent_priority_stages():
    now = datetime.now().astimezone()
    # Vence en 14 minutos -> debe disparar stage '15m'
    target_15m = now + timedelta(minutes=14)
    db = SessionLocal()
    rem = ReminderModel(
        title="Reunión Urgente",
        target_datetime_iso=target_15m.isoformat(),
        priority="URGENT",
        status="PENDING",
        stages_notified=""
    )
    db.add(rem)
    db.commit()
    rem_id = rem.id
    db.close()

    notifications = NotificationEngine.check_and_notify_due_reminders(reference_now=now)
    assert any(n["reminder_id"] == rem_id and n["stage"] == "15m" for n in notifications)

def test_snooze_functionality():
    now = datetime.now().astimezone()
    res = memory_manager.create_reminder("Estudiar matemáticas", "en 1 minuto", priority="NORMAL")
    rem_id = res["data"]["id"]

    snooze_res = memory_manager.snooze_reminder(rem_id, minutes=20)
    assert snooze_res["success"] is True
    assert snooze_res["data"]["status"] == "SNOOZED"

def test_pending_summary():
    summary = memory_manager.get_pending_summary()
    assert "total_pending" in summary
    assert "summary_text" in summary
    assert isinstance(summary["reminders"], list)

def test_notification_channels_multichannel_dispatch():
    from core.notification_engine import NotificationChannel, DesktopNotificationChannel, WebPushNotificationChannel
    
    desktop_ch = DesktopNotificationChannel()
    webpush_ch = WebPushNotificationChannel()
    
    assert isinstance(desktop_ch, NotificationChannel)
    assert isinstance(webpush_ch, NotificationChannel)
    
    # Desktop channel send
    d_res = desktop_ch.send("Test", "Desktop test msg", priority="NORMAL")
    assert d_res is True
    
    # Web push channel stub returns False and logs stub info without crashing
    w_res = webpush_ch.send("Test", "WebPush stub msg", priority="NORMAL")
    assert w_res is False
    
    # Multichannel dispatch through NotificationEngine
    results = NotificationEngine.dispatch_notification("Alerta Global", "Mensaje de prueba multicanal")
    assert "DesktopNotificationChannel" in results
    assert "WebPushNotificationChannel" in results
    assert results["DesktopNotificationChannel"] is True
    assert results["WebPushNotificationChannel"] is False
