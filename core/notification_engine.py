import asyncio
import os
import sys
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Callable
from core.database import SessionLocal, ReminderModel
from core.logger import logger
from core.config import settings

from abc import ABC, abstractmethod

class NotificationChannel(ABC):
    """
    Interfaz abstracta para canales de notificación desacoplados de la plataforma (A.1).
    Permite despachar alertas tanto en escritorio como en entornos móviles o web push.
    """
    @abstractmethod
    def send(self, title: str, message: str, priority: str = "NORMAL", metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Envía una notificación a través del canal específico."""
        pass

class DesktopNotificationChannel(NotificationChannel):
    """
    Canal nativo de escritorio (Windows Toast / plyer / winotify / winsound).
    """
    def send(self, title: str, message: str, priority: str = "NORMAL", metadata: Optional[Dict[str, Any]] = None) -> bool:
        # 1. Alerta de sonido nativa
        try:
            import winsound
            if priority.upper() in ["URGENT", "HIGH"]:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            else:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass

        # 2. Notificación visual mediante plyer
        try:
            from plyer import notification
            notification.notify(
                app_name="JARVIS Assistant",
                title=f"JARVIS — {title}",
                message=message,
                timeout=8
            )
            logger.info(f"[DesktopNotificationChannel] Notificación nativa plyer enviada: {title}")
            return True
        except Exception as pe:
            logger.debug(f"[DesktopNotificationChannel] Fallback desde plyer: {pe}")

        try:
            from winotify import Notification, audio
            sound = audio.Default
            if priority == "URGENT":
                sound = audio.LoopingAlarm
            elif priority == "HIGH":
                sound = audio.Reminder

            toast = Notification(
                app_id="JARVIS Assistant",
                title=f"JARVIS — {title}",
                msg=message,
                duration="short"
            )
            toast.set_audio(sound, loop=False)
            toast.show()
            logger.info(f"[DesktopNotificationChannel] Toast Windows enviado: {title} | {message}")
            return True
        except Exception as e:
            try:
                import subprocess
                ps_script = f"""
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
                [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
                $template = @"
                <toast>
                    <visual>
                        <binding template='ToastGeneric'>
                            <text>JARVIS — {title}</text>
                            <text>{message}</text>
                        </binding>
                    </visual>
                </toast>
"@
                $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
                $xml.LoadXml($template)
                $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
                $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('JARVIS.Assistant')
                $notifier.Show($toast)
                """
                subprocess.Popen(["powershell", "-Command", ps_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logger.info(f"[DesktopNotificationChannel] Toast PowerShell enviado: {title}")
                return True
            except Exception as pe:
                logger.error(f"[DesktopNotificationChannel] Error enviando notificación: {pe}")
                return False

class WebPushNotificationChannel(NotificationChannel):
    """
    Canal de notificación para Web Push (PWA/Mobile).
    Stub documentado para futuras suscripciones Push API (VAPID / FCM)
    cuando JARVIS se empaquete para móvil o active notificaciones en navegador.
    """
    def send(self, title: str, message: str, priority: str = "NORMAL", metadata: Optional[Dict[str, Any]] = None) -> bool:
        logger.info(f"[WebPushNotificationChannel] [STUB] Push notification para móvil no implementada aún: '{title}' - '{message}'")
        return False

class NotificationEngine:
    """
    Motor autónomo de notificaciones para JARVIS (BUG-31):
    - Evalúa recordatorios pendientes en background.
    - Dispara notificaciones a través de los canales registrados (Desktop / WebPush).
    - Transmite eventos en vivo vía WebSocket a clientes web activos.
    - Ejecuta recuperación catch-up de recordatorios vencidos offline.
    - Evita duplicados mediante el registro de stages_notified.
    """
    
    _history: List[Dict[str, Any]] = []
    _broadcast_callbacks: List[Callable[[Dict[str, Any]], Any]] = []
    _channels: List[NotificationChannel] = [
        DesktopNotificationChannel(),
        WebPushNotificationChannel()
    ]

    @classmethod
    def register_channel(cls, channel: NotificationChannel):
        """Registra un nuevo canal de notificación."""
        if channel not in cls._channels:
            cls._channels.append(channel)

    @classmethod
    def register_broadcast_callback(cls, callback: Callable[[Dict[str, Any]], Any]):
        """Registra un callback para transmitir eventos de alarma a WebSockets activos."""
        if callback not in cls._broadcast_callbacks:
            cls._broadcast_callbacks.append(callback)

    @classmethod
    def send_native_toast(cls, title: str, message: str, priority: str = "NORMAL", metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Envía una notificación nativa del sistema operativo mediante DesktopNotificationChannel.
        Mantiene compatibilidad total con llamadas anteriores.
        """
        desktop_ch = next((c for c in cls._channels if isinstance(c, DesktopNotificationChannel)), None)
        if desktop_ch:
            return desktop_ch.send(title, message, priority, metadata)
        return DesktopNotificationChannel().send(title, message, priority, metadata)

    @classmethod
    def dispatch_notification(cls, title: str, message: str, priority: str = "NORMAL", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, bool]:
        """
        Despacha la alerta a todos los canales disponibles (Desktop, WebPush, etc.).
        """
        results = {}
        for channel in cls._channels:
            c_name = channel.__class__.__name__
            try:
                results[c_name] = channel.send(title, message, priority, metadata)
            except Exception as e:
                logger.warning(f"[NotificationEngine] Error en canal {c_name}: {e}")
                results[c_name] = False
        return results

    @classmethod
    def check_and_notify_due_reminders(cls, reference_now: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Evalúa los recordatorios en la base de datos y dispara los avisos correspondientes.
        Incluye soporte para recordatorios exactos, etapas previas y catch-up de recordatorios vencidos offline.
        """
        now = reference_now or datetime.now().astimezone()
        if now.tzinfo is None:
            now = now.astimezone()
        db = SessionLocal()
        notifications_sent = []

        try:
            reminders = db.query(ReminderModel).filter(
                ReminderModel.status.in_(["PENDING", "SNOOZED"])
            ).all()

            for rem in reminders:
                try:
                    target_dt = datetime.fromisoformat(rem.target_datetime_iso)
                    if target_dt.tzinfo is None:
                        target_dt = target_dt.replace(tzinfo=now.tzinfo)
                except Exception as parse_err:
                    logger.warning(f"[NotificationEngine] Error parseando fecha de recordatorio #{rem.id}: {parse_err}")
                    continue

                diff_seconds = (target_dt - now).total_seconds()
                diff_minutes = diff_seconds / 60.0
                priority = (rem.priority or "NORMAL").upper()
                stages = set(rem.stages_notified.split(",")) if rem.stages_notified else set()

                should_notify = False
                stage_tag = None
                notification_msg = ""

                # --- EVALUACIÓN DE ESTRATEGIA SEGÚN PRIORIDAD Y CATCH-UP ---
                # Si la hora ya pasó (diff_minutes <= 0.05) y no se había notificado exactamente
                if diff_minutes <= 0.05 and "exact" not in stages:
                    stage_tag = "exact"
                    should_notify = True
                    if diff_minutes < -1.0:
                        # Catch-up (venció mientras estaba offline o en espera)
                        notification_msg = f"Recordatorio pendiente: {rem.title} ({rem.display_datetime})"
                    else:
                        notification_msg = f"¡Momento de: {rem.title}!" if priority in ["HIGH", "URGENT"] else f"Recordatorio: {rem.title}"
                    
                    if rem.is_recurring and rem.recurrence_rule:
                        # Calcular y avanzar a la siguiente ocurrencia
                        from core.reminders import advance_recurrence, reminder_engine
                        next_dt = advance_recurrence(rem.recurrence_rule, rem.target_datetime_iso)
                        if next_dt:
                            rem.target_datetime_iso = next_dt.isoformat()
                            rem.display_datetime = next_dt.strftime("%A, %d de %B de %Y a las %I:%M %p")
                            rem.stages_notified = ""
                            rem.status = "PENDING"
                            try:
                                reminder_engine.sync_job_for_reminder(rem)
                            except Exception:
                                pass
                        else:
                            rem.status = "NOTIFIED"
                    else:
                        rem.status = "NOTIFIED"

                elif priority == "URGENT":
                    if 0.05 < diff_minutes <= 15 and "15m" not in stages:
                        stage_tag = "15m"
                        should_notify = True
                        notification_msg = f"En 15 minutos: {rem.title}"
                    elif 15 < diff_minutes <= 60 and "1h" not in stages:
                        stage_tag = "1h"
                        should_notify = True
                        notification_msg = f"En 1 hora: {rem.title}"
                    elif 60 < diff_minutes <= 180 and "3h" not in stages:
                        stage_tag = "3h"
                        should_notify = True
                        notification_msg = f"En 3 horas: {rem.title}"

                elif priority == "HIGH":
                    if 0.05 < diff_minutes <= 15 and "15m" not in stages:
                        stage_tag = "15m"
                        should_notify = True
                        notification_msg = f"En 15 minutos: {rem.title}"
                    elif 15 < diff_minutes <= 60 and "1h" not in stages:
                        stage_tag = "1h"
                        should_notify = True
                        notification_msg = f"En 1 hora: {rem.title}"

                elif priority == "NORMAL":
                    if 0.05 < diff_minutes <= 15 and "15m" not in stages:
                        stage_tag = "15m"
                        should_notify = True
                        notification_msg = f"En 15 minutos: {rem.title}"

                if diff_minutes < -1440 and rem.status != "COMPLETED":
                    rem.status = "MISSED"

                if should_notify and stage_tag:
                    if not (rem.is_recurring and rem.recurrence_rule and stage_tag == "exact"):
                        stages.add(stage_tag)
                        rem.stages_notified = ",".join(sorted(stages))
                    rem.updated_at = datetime.now(timezone.utc)
                    
                    # 1. Disparo de notificaciones multicanal (Desktop, WebPush Stub)
                    cls.dispatch_notification(
                        title=f"Recordatorio ({priority})",
                        message=notification_msg,
                        priority=priority,
                        metadata={"reminder_id": rem.id, "stage": stage_tag}
                    )

                    notif_data = {
                        "reminder_id": rem.id,
                        "title": rem.title,
                        "message": notification_msg,
                        "display_datetime": rem.display_datetime,
                        "stage": stage_tag,
                        "priority": priority,
                        "timestamp": now.isoformat()
                    }
                    cls._history.append(notif_data)
                    notifications_sent.append(notif_data)

                    # 2. Transmisión a WebSockets activos
                    for cb in cls._broadcast_callbacks:
                        try:
                            cb(notif_data)
                        except Exception as cb_err:
                            logger.warning(f"[NotificationEngine] Error en broadcast callback: {cb_err}")

            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"[NotificationEngine] Error en ciclo de evaluación: {e}")
        finally:
            db.close()

        return notifications_sent

class ReminderScheduler:
    """
    Planificador de fondo para supervisión continua de recordatorios.
    """
    _running: bool = False
    _task: Optional[asyncio.Task] = None

    @classmethod
    async def start(cls, interval_seconds: int = 5):
        if cls._running:
            return
        cls._running = True
        logger.info("[ReminderScheduler] Motor de fondo iniciado.")
        
        while cls._running:
            try:
                NotificationEngine.check_and_notify_due_reminders()
            except Exception as e:
                logger.error(f"[ReminderScheduler] Error en ciclo: {e}")
            await asyncio.sleep(interval_seconds)

    @classmethod
    def stop(cls):
        cls._running = False
        logger.info("[ReminderScheduler] Motor de fondo detenido.")
