import re
import os
import sys
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple, Callable

import dateparser
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

from core.database import SessionLocal, ReminderModel, engine, init_db
from core.config import settings
from core.logger import logger

# Mapeo de días de la semana en español e inglés
WEEKDAYS_MAP = {
    'lunes': 'mon', 'monday': 'mon',
    'martes': 'tue', 'tuesday': 'tue',
    'miercoles': 'wed', 'miércoles': 'wed', 'wednesday': 'wed',
    'jueves': 'thu', 'thursday': 'thu',
    'viernes': 'fri', 'friday': 'fri',
    'sabado': 'sat', 'sábado': 'sat', 'saturday': 'sat',
    'domingo': 'sun', 'sunday': 'sun'
}

def send_native_notification(title: str, message: str, priority: str = "NORMAL") -> bool:
    """
    Envía una notificación nativa al sistema operativo utilizando plyer
    con sonido nativo y alerta visual independiente de la interfaz web.
    """
    priority_upper = (priority or "NORMAL").upper()

    # 1. Alerta sonora nativa del sistema operativo
    try:
        import winsound
        if priority_upper in ["URGENT", "HIGH"]:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        else:
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
    except Exception as e:
        logger.debug(f"[Reminders] Alerta sonora omitida o no soportada: {e}")

    # 2. Notificación visual mediante plyer
    plyer_success = False
    try:
        from plyer import notification
        notification.notify(
            title=f"JARVIS — {title}",
            message=message,
            app_name="JARVIS Assistant",
            timeout=8
        )
        plyer_success = True
        logger.info(f"[Reminders] Notificación plyer enviada: {title}")
    except Exception as pe:
        logger.debug(f"[Reminders] Fallback desde plyer por: {pe}")

    # 3. Fallback de respaldo con Windows Toast / PowerShell
    if not plyer_success:
        try:
            from core.notification_engine import NotificationEngine
            NotificationEngine.send_native_toast(title=title, message=message, priority=priority_upper)
        except Exception as fe:
            logger.warning(f"[Reminders] Error en fallback de notificación: {fe}")

    return True

def advance_recurrence(rule: str, current_target_iso: Optional[str] = None) -> Optional[datetime]:
    """Calcula la siguiente fecha objetivo para un recordatorio recurrente."""
    now = datetime.now().astimezone()
    try:
        base_dt = datetime.fromisoformat(current_target_iso) if current_target_iso else now
        if base_dt.tzinfo is None:
            base_dt = base_dt.replace(tzinfo=now.tzinfo)
    except Exception:
        base_dt = now

    r_low = (rule or "").lower()

    # 1. cada X minutos
    m_min = re.search(r'cada\s+(\d+)\s+min(?:uto)?s?', r_low)
    if m_min:
        mins = int(m_min.group(1))
        next_dt = base_dt + timedelta(minutes=mins)
        while next_dt <= now:
            next_dt += timedelta(minutes=mins)
        return next_dt

    # 2. cada X horas
    m_hr = re.search(r'cada\s+(\d+)\s+horas?', r_low)
    if m_hr:
        hrs = int(m_hr.group(1))
        next_dt = base_dt + timedelta(hours=hrs)
        while next_dt <= now:
            next_dt += timedelta(hours=hrs)
        return next_dt

    # 3. todos los días / cada día / diariamente
    if any(k in r_low for k in ["cada dia", "cada día", "diariamente", "todos los dias", "todos los días"]):
        next_dt = base_dt + timedelta(days=1)
        while next_dt <= now:
            next_dt += timedelta(days=1)
        return next_dt

    # 4. cada [día de semana]
    next_dt = base_dt + timedelta(days=7)
    while next_dt <= now:
        next_dt += timedelta(days=7)
    return next_dt

def _job_dispatch_callback(reminder_id: int, title: str, message: str, priority: str, is_recurring: bool):
    """
    Función de ejecución autónoma invocada por APScheduler al vencer el recordatorio.
    """
    db = SessionLocal()
    try:
        rem = db.query(ReminderModel).filter(ReminderModel.id == reminder_id).first()
        if not rem or rem.status not in ["PENDING", "SNOOZED"]:
            return

        stages = set(rem.stages_notified.split(",")) if rem.stages_notified else set()
        if "exact" in stages:
            # Ya fue notificado previamente por NotificationEngine
            return

        logger.info(f"[Reminders Job] ¡Alarma disparada! #{reminder_id}: {title}")
        
        # 1. Notificación nativa SO (Plyer + Audio)
        send_native_notification(title=title, message=message, priority=priority)

        # 2. Transmisión a WebSockets activos
        notif_data = {
            "reminder_id": reminder_id,
            "title": title,
            "message": message,
            "priority": priority,
            "is_recurring": is_recurring,
            "timestamp": datetime.now().astimezone().isoformat()
        }
        try:
            from core.notification_engine import NotificationEngine
            NotificationEngine._history.append(notif_data)
            for cb in NotificationEngine._broadcast_callbacks:
                try:
                    cb(notif_data)
                except Exception as cb_err:
                    logger.warning(f"[Reminders Job] Error en callback de broadcast: {cb_err}")
        except Exception as e:
            logger.debug(f"[Reminders Job] Error notificando WebSockets: {e}")

        # 3. Actualización de estado en base de datos SQLite
        stages.add("exact")
        rem.stages_notified = ",".join(sorted(stages))
        if is_recurring and rem.recurrence_rule:
            next_dt = advance_recurrence(rem.recurrence_rule, rem.target_datetime_iso)
            if next_dt:
                rem.target_datetime_iso = next_dt.isoformat()
                rem.display_datetime = next_dt.strftime("%A, %d de %B de %Y a las %I:%M %p")
                rem.stages_notified = ""
                rem.status = "PENDING"
            else:
                rem.status = "NOTIFIED"
        else:
            rem.status = "NOTIFIED"
        rem.updated_at = datetime.now(timezone.utc)
        db.commit()
    except Exception as db_err:
        db.rollback()
        logger.error(f"[Reminders Job] Error actualizando BD #{reminder_id}: {db_err}")
    finally:
        db.close()

class ReminderEngine:
    """
    Motor integral de tiempo y recordatorios persistentes para JARVIS v3.1:
    - Programador robusto con APScheduler persistido en SQLite.
    - Soporte completo para tareas puntuales y recurrentes.
    - Parseo de lenguaje natural con dateparser y expresiones en español.
    - Disparo de alertas nativas con plyer y sonido.
    """

    def __init__(self):
        init_db()
        self._scheduler: Optional[BackgroundScheduler] = None
        self._is_running: bool = False

    def start(self):
        """Inicia el planificador de APScheduler con persistencia en SQLite."""
        if self._is_running and self._scheduler:
            return

        jobstores = {
            'default': SQLAlchemyJobStore(engine=engine, tablename="apscheduler_jobs")
        }
        job_defaults = {
            'coalesce': True,
            'max_instances': 3,
            'misfire_grace_time': 300
        }

        self._scheduler = BackgroundScheduler(jobstores=jobstores, job_defaults=job_defaults)
        self._scheduler.start()
        self._is_running = True
        logger.info("[ReminderEngine] APScheduler iniciado con persistencia en SQLite.")
        self.sync_jobs_from_db()

    def stop(self):
        """Detiene el planificador de forma segura."""
        if self._scheduler and self._is_running:
            self._scheduler.shutdown(wait=False)
            self._is_running = False
            logger.info("[ReminderEngine] APScheduler detenido.")

    def parse_time_expression(self, expression: str) -> Tuple[Optional[Any], bool, Optional[datetime], str]:
        """
        Interpreta expresiones en lenguaje natural para programar tareas recurrentes o puntuales.
        Retorna (trigger, is_recurring, target_dt, display_str).
        """
        expr_raw = (expression or "").strip()
        expr_low = expr_raw.lower()
        now = datetime.now().astimezone()

        # ----------------------------------------------------------------------
        # 1. EVALUAR PATRONES RECURRENTES
        # ----------------------------------------------------------------------
        # 'cada lunes a las 9am', 'todos los viernes a las 18:00'
        m_day = re.search(r'(?:cada|todos los)\s+([a-záéíóúñ]+)\s+a\s+las?\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', expr_low)
        if m_day:
            day_str, hour, minute, ampm = m_day.groups()
            clean_day = day_str.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
            if clean_day in WEEKDAYS_MAP:
                h = int(hour)
                m = int(minute or 0)
                if ampm == 'pm' and h < 12: h += 12
                elif ampm == 'am' and h == 12: h = 0
                cron = CronTrigger(day_of_week=WEEKDAYS_MAP[clean_day], hour=h, minute=m)
                disp = f"Cada {day_str.capitalize()} a las {h:02d}:{m:02d}"
                return cron, True, None, disp

        # 'cada día a las 8am', 'todos los días a las 8:00', 'diariamente a las 10:30'
        m_daily = re.search(r'(?:cada d[ií]a|diariamente|todos los d[ií]as)\s+a\s+las?\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', expr_low)
        if m_daily:
            hour, minute, ampm = m_daily.groups()
            h = int(hour)
            m = int(minute or 0)
            if ampm == 'pm' and h < 12: h += 12
            elif ampm == 'am' and h == 12: h = 0
            cron = CronTrigger(hour=h, minute=m)
            disp = f"Todos los días a las {h:02d}:{m:02d}"
            return cron, True, None, disp

        # 'cada X minutos' o 'cada X horas'
        m_interval_m = re.search(r'cada\s+(\d+)\s+minuto', expr_low)
        if m_interval_m:
            mins = int(m_interval_m.group(1))
            return IntervalTrigger(minutes=mins), True, None, f"Cada {mins} minutos"

        m_interval_h = re.search(r'cada\s+(\d+)\s+hora', expr_low)
        if m_interval_h:
            hrs = int(m_interval_h.group(1))
            return IntervalTrigger(hours=hrs), True, None, f"Cada {hrs} horas"

        # ----------------------------------------------------------------------
        # 2. EVALUAR RECORDATORIOS PUNTUALES CON DATEPARSER
        # ----------------------------------------------------------------------
        tz_str = settings.TIMEZONE_OVERRIDE or "America/Bogota"
        parsed_dt = dateparser.parse(
            expr_raw,
            languages=['es', 'en'],
            settings={
                'PREFER_DATES_FROM': 'future',
                'TIMEZONE': tz_str,
                'RETURN_AS_TIMEZONE_AWARE': True
            }
        )

        # Si dateparser no reconoció la expresión, recurrir a TimeParser existente
        if not parsed_dt:
            from core.time_parser import TimeParser
            try:
                res = TimeParser.parse(expr_raw, reference_dt=now)
                if res and res.get("success") and res.get("datetime_iso"):
                    parsed_dt = datetime.fromisoformat(res["datetime_iso"])
            except Exception:
                pass

        if parsed_dt:
            if parsed_dt.tzinfo is None:
                parsed_dt = parsed_dt.replace(tzinfo=now.tzinfo)

            # Si la fecha parseada quedó en el pasado por margen de segundos, ajustar al presente inmediato
            if (parsed_dt - now).total_seconds() < -1:
                if (now - parsed_dt).total_seconds() < 120:
                    parsed_dt = now + timedelta(seconds=5)

            disp = parsed_dt.strftime("%A, %d de %B de %Y a las %I:%M %p")
            trigger = DateTrigger(run_date=parsed_dt)
            return trigger, False, parsed_dt, disp

        return None, False, None, expr_raw

    def schedule_reminder(
        self,
        title: str,
        time_expression: str,
        priority: str = "NORMAL",
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Programa un recordatorio persistente en SQLite tanto puntual como recurrente.
        """
        if not self._is_running:
            self.start()

        trigger, is_recurring, target_dt, display_str = self.parse_time_expression(time_expression)
        if not trigger:
            return {
                "success": False,
                "data": {},
                "error": f"No pude interpretar la fecha u hora en: '{time_expression}'"
            }

        target_iso = target_dt.isoformat() if target_dt else datetime.now().astimezone().isoformat()
        db = SessionLocal()
        try:
            rem = ReminderModel(
                title=title,
                description=description or "",
                target_datetime_iso=target_iso,
                display_datetime=display_str,
                priority=priority.upper(),
                status="PENDING",
                stages_notified="",
                is_recurring=is_recurring,
                recurrence_rule=time_expression if is_recurring else None
            )
            db.add(rem)
            db.commit()
            db.refresh(rem)
            rem_id = rem.id

            # Programar job en APScheduler (persistido en SQLite)
            job_id = f"jarvis_reminder_{rem_id}"
            msg = f"Momento de: {title}" if priority.upper() in ["URGENT", "HIGH"] else f"Recordatorio: {title}"
            
            self._scheduler.add_job(
                _job_dispatch_callback,
                trigger=trigger,
                args=[rem_id, title, msg, priority.upper(), is_recurring],
                id=job_id,
                name=title,
                replace_existing=True
            )

            logger.info(f"[ReminderEngine] Recordatorio #{rem_id} ({display_str}) registrado en APScheduler.")

            return {
                "success": True,
                "data": {
                    "id": rem_id,
                    "title": title,
                    "display_datetime": display_str,
                    "target_datetime_iso": target_iso,
                    "priority": priority.upper(),
                    "is_recurring": is_recurring,
                    "status": "PENDING"
                },
                "error": None
            }
        except Exception as e:
            db.rollback()
            logger.error(f"[ReminderEngine] Error programando recordatorio: {e}")
            return {"success": False, "data": {}, "error": str(e)}
        finally:
            db.close()

    def sync_jobs_from_db(self):
        """
        Sincroniza y recarga recordatorios activos desde SQLite en APScheduler al iniciar el servidor.
        """
        if not self._scheduler:
            return

        db = SessionLocal()
        try:
            pending_reminders = db.query(ReminderModel).filter(
                ReminderModel.status.in_(["PENDING", "SNOOZED"])
            ).all()

            for rem in pending_reminders:
                job_id = f"jarvis_reminder_{rem.id}"
                if self._scheduler.get_job(job_id):
                    continue

                if rem.is_recurring and rem.recurrence_rule:
                    trigger, is_rec, _, disp = self.parse_time_expression(rem.recurrence_rule)
                else:
                    try:
                        target_dt = datetime.fromisoformat(rem.target_datetime_iso)
                        now = datetime.now().astimezone()
                        if target_dt.tzinfo is None:
                            target_dt = target_dt.replace(tzinfo=now.tzinfo)
                        if target_dt < now:
                            continue
                        trigger = DateTrigger(run_date=target_dt)
                        is_rec = False
                    except Exception:
                        continue

                if trigger:
                    msg = f"Momento de: {rem.title}"
                    self._scheduler.add_job(
                        _job_dispatch_callback,
                        trigger=trigger,
                        args=[rem.id, rem.title, msg, (rem.priority or "NORMAL").upper(), is_rec],
                        id=job_id,
                        name=rem.title,
                        replace_existing=True
                    )
            logger.info(f"[ReminderEngine] Sincronizados {len(pending_reminders)} recordatorios pendientes.")
        except Exception as e:
            logger.error(f"[ReminderEngine] Error sincronizando jobs desde BD: {e}")
        finally:
            db.close()

    def sync_job_for_reminder(self, rem: ReminderModel):
        """Programa o actualiza un job en APScheduler para un ReminderModel."""
        if not self._scheduler:
            return
        job_id = f"jarvis_reminder_{rem.id}"
        
        # Eliminar si ya existía para actualizar
        try:
            if self._scheduler.get_job(job_id):
                self._scheduler.remove_job(job_id)
        except Exception:
            pass

        if rem.status not in ["PENDING", "SNOOZED"]:
            return

        if rem.is_recurring and rem.recurrence_rule:
            trigger, is_rec, _, _ = self.parse_time_expression(rem.recurrence_rule)
        else:
            try:
                target_dt = datetime.fromisoformat(rem.target_datetime_iso)
                now = datetime.now().astimezone()
                if target_dt.tzinfo is None:
                    target_dt = target_dt.replace(tzinfo=now.tzinfo)
                if target_dt < now:
                    return
                trigger = DateTrigger(run_date=target_dt)
                is_rec = False
            except Exception:
                return

        if trigger:
            msg = f"Momento de: {rem.title}"
            try:
                self._scheduler.add_job(
                    _job_dispatch_callback,
                    trigger=trigger,
                    args=[rem.id, rem.title, msg, (rem.priority or "NORMAL").upper(), is_rec],
                    id=job_id,
                    name=rem.title,
                    replace_existing=True
                )
                logger.info(f"[ReminderEngine] Job #{rem.id} ('{rem.title}') sincronizado en APScheduler.")
            except Exception as e_add:
                logger.warning(f"[ReminderEngine] Error agregando job #{rem.id} a APScheduler: {e_add}")

    def remove_job_for_reminder(self, reminder_id: int):
        """Remueve un job de APScheduler por ID de recordatorio."""
        if not self._scheduler:
            return
        job_id = f"jarvis_reminder_{reminder_id}"
        try:
            if self._scheduler.get_job(job_id):
                self._scheduler.remove_job(job_id)
                logger.info(f"[ReminderEngine] Job #{reminder_id} removido de APScheduler.")
        except Exception:
            pass

    def clear_all_jobs(self):
        """Remueve todos los jobs del scheduler gestionados por JARVIS."""
        if not self._scheduler:
            return
        try:
            for job in self._scheduler.get_jobs():
                if job.id.startswith("jarvis_reminder_"):
                    self._scheduler.remove_job(job.id)
            logger.info("[ReminderEngine] Todos los jobs de recordatorios removidos de APScheduler.")
        except Exception:
            pass

    def cancel_reminder(self, reminder_id: int) -> bool:
        """Cancela y remueve un recordatorio del planificador y la base de datos."""
        self.remove_job_for_reminder(reminder_id)

        db = SessionLocal()
        try:
            rem = db.query(ReminderModel).filter(ReminderModel.id == reminder_id).first()
            if rem:
                rem.status = "CANCELLED"
                rem.updated_at = datetime.now(timezone.utc)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            return False
        finally:
            db.close()

# Instancia singleton global
reminder_engine = ReminderEngine()

