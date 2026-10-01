import json
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from core.database import SessionLocal, MemoryModel, SemanticMemoryModel, TaskModel, ReminderModel, UserProfileModel, init_db
from core.config import settings
from core.logger import logger
from core.time_parser import TimeParser
from core.user_profile import UserProfile, PersonalityProfile
from core.memory_retriever import MemoryRetriever
from core.semantic_vectorizer import LocalSemanticVectorizer

class MemoryType:
    CONVERSATION = "CONVERSATION"
    PERSONAL = "PERSONAL"
    PREFERENCE = "PREFERENCE"
    HABIT = "HABIT"
    PROJECT = "PROJECT"
    TASK_CONTEXT = "TASK_CONTEXT"
    MEDIA_PREFERENCE = "MEDIA_PREFERENCE"
    SYSTEM_PREFERENCE = "SYSTEM_PREFERENCE"

class MemoryManager:
    """
    Gestor de memoria personal unificado (Fuente Única de Verdad).
    """
    def __init__(self):
        init_db()
        self.supabase = None
        self.user_profile = UserProfile()
        self._init_supabase()
        self._load_user_profile()

    def _init_supabase(self):
        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            try:
                from supabase import create_client
                self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                logger.info("[Memoria] Cliente Supabase conectado con éxito.")
            except Exception as e:
                logger.warning(f"[Memoria] Supabase no disponible ({e}). Operando en SQLite local.")
                self.supabase = None

    def _load_user_profile(self):
        db = SessionLocal()
        try:
            rows = db.query(UserProfileModel).all()
            profile_map = {r.key: r.value for r in rows}

            # full_name tiene prioridad sobre name y user_name
            if "full_name" in profile_map:
                self.user_profile.name = profile_map["full_name"]
            elif "name" in profile_map:
                self.user_profile.name = profile_map["name"]
            elif "user_name" in profile_map:
                self.user_profile.name = profile_map["user_name"]
        except Exception:
            pass
        finally:
            db.close()

    def set_profile(self, key: str, value: Any):
        val_str = json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else str(value)
        db = SessionLocal()
        try:
            item = db.query(UserProfileModel).filter(UserProfileModel.key == key).first()
            if item:
                item.value = val_str
                item.updated_at = datetime.now(timezone.utc)
            else:
                db.add(UserProfileModel(key=key, value=val_str))
            db.commit()
            # Actualizar caché en memoria
            if key in ("name", "full_name"):
                self.user_profile.name = val_str
        except Exception as e:
            db.rollback()
            logger.error(f"[Memoria] Error guardando perfil: {e}")
        finally:
            db.close()

    def get_all_profile(self) -> Dict[str, Any]:
        db = SessionLocal()
        profile = self.user_profile.to_dict()
        try:
            rows = db.query(UserProfileModel).all()
            for r in rows:
                try:
                    profile[r.key] = json.loads(r.value)
                except Exception:
                    profile[r.key] = r.value
        finally:
            db.close()
        return profile

    def store_memory(
        self,
        key: str,
        value: str,
        mem_type: str = MemoryType.PERSONAL,
        category: str = "general",
        confidence: float = 0.9,
        importance: float = 0.5,
        source: str = "user_explicit",
        tags: str = ""
    ) -> Dict[str, Any]:
        clean_key = key.lower().strip()
        db = SessionLocal()
        try:
            existing = db.query(MemoryModel).filter(MemoryModel.key == clean_key, MemoryModel.active == True).first()
            if existing:
                existing.value = value
                existing.type = mem_type
                existing.category = category
                existing.confidence = confidence
                existing.importance = importance
                existing.source = source
                existing.tags = tags
                existing.updated_at = datetime.now(timezone.utc)
                existing.last_used_at = datetime.now(timezone.utc)
                mem_id = existing.id
            else:
                new_mem = MemoryModel(
                    key=clean_key,
                    value=value,
                    type=mem_type,
                    category=category,
                    confidence=confidence,
                    importance=importance,
                    source=source,
                    tags=tags,
                    active=True
                )
                db.add(new_mem)
                db.commit()
                db.refresh(new_mem)
                mem_id = new_mem.id

            # Sincronización aditiva con semantic_memories (Roadmap Fase D)
            try:
                vec = LocalSemanticVectorizer.vectorize(f"{clean_key} {value} {tags}")
                sem_exist = db.query(SemanticMemoryModel).filter(
                    SemanticMemoryModel.key == clean_key,
                    SemanticMemoryModel.active == True
                ).first()
                if sem_exist:
                    sem_exist.value = value
                    sem_exist.memory_type = mem_type
                    sem_exist.category = category
                    sem_exist.confidence = confidence
                    sem_exist.importance = importance
                    sem_exist.tags = json.dumps(tags.split() if isinstance(tags, str) else tags)
                    sem_exist.embedding = json.dumps(vec)
                    sem_exist.reinforcement_count = (sem_exist.reinforcement_count or 0) + 1
                    sem_exist.last_accessed_at = datetime.now(timezone.utc)
                else:
                    sem_new = SemanticMemoryModel(
                        entry_id=f"sem_{clean_key}_{int(datetime.now(timezone.utc).timestamp())}",
                        key=clean_key,
                        value=value,
                        memory_type=mem_type,
                        category=category,
                        confidence=confidence,
                        importance=importance,
                        tags=json.dumps(tags.split() if isinstance(tags, str) else tags),
                        embedding=json.dumps(vec),
                        active=True
                    )
                    db.add(sem_new)
            except Exception as ex_sem:
                logger.warning(f"[Memoria] Error sincronizando memoria semántica: {ex_sem}")

            db.commit()
            logger.info(f"[MEMORY WRITE] Guardado recuerdo #{mem_id}: {clean_key} = {value}")
            return {"success": True, "id": mem_id, "key": clean_key, "value": value, "type": mem_type}
        except Exception as e:
            db.rollback()
            logger.error(f"[Memoria] Error almacenando recuerdo: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def recall_memories(self, category: Optional[str] = None, mem_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        db = SessionLocal()
        try:
            q = db.query(MemoryModel).filter(MemoryModel.active == True)
            if mem_type:
                q = q.filter(MemoryModel.type == mem_type)
            elif category:
                q = q.filter(MemoryModel.category == category)
            rows = q.order_by(MemoryModel.id.desc()).limit(limit).all()
            return [
                {
                    "id": r.id,
                    "key": r.key,
                    "value": r.value,
                    "type": r.type,
                    "category": r.category,
                    "confidence": r.confidence,
                    "importance": r.importance,
                    "tags": getattr(r, "tags", "") or "",
                    "active": r.active,
                    "created_at": r.created_at,
                    "updated_at": r.updated_at,
                    "last_used_at": r.last_used_at
                }
                for r in rows
            ]
        finally:
            db.close()

    def get_contextual_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        all_mems = self.recall_memories(limit=500)
        return MemoryRetriever.retrieve_relevant(all_mems, query, limit=limit)

    def forget_memory(self, key_or_query: str) -> Dict[str, Any]:
        clean_q = key_or_query.lower().strip()
        q_norm = clean_q.replace("_", "").replace(" ", "").replace("mi", "").replace("favorito", "").strip()
        db = SessionLocal()
        count = 0
        try:
            mems = db.query(MemoryModel).filter(MemoryModel.active == True).all()
            for m in mems:
                k_norm = m.key.lower().replace("_", "").replace(" ", "").strip()
                v_norm = m.value.lower().strip()
                
                if (clean_q in m.key.lower() or 
                    clean_q in v_norm or 
                    (q_norm and q_norm in k_norm) or 
                    (q_norm and q_norm in v_norm) or
                    (k_norm and k_norm in clean_q)):
                    m.active = False
                    m.updated_at = datetime.now(timezone.utc)
                    count += 1

            # Desactivar en semantic_memories (Fase D)
            try:
                db.query(SemanticMemoryModel).filter(
                    SemanticMemoryModel.key == clean_q,
                    SemanticMemoryModel.active == True
                ).update({"active": False})
            except Exception:
                pass

            db.commit()
            logger.info(f"[MEMORY DELETE] Eliminados {count} recuerdos coincidentes con '{key_or_query}'")
            return {
                "success": True,
                "forgotten_count": count,
                "message": f"Olvidé la información sobre '{key_or_query}'." if count > 0 else f"No tengo registrada información sobre '{key_or_query}' para olvidar."
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def clear_all_memory(self) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            db.query(MemoryModel).update({"active": False})
            try:
                db.query(SemanticMemoryModel).update({"active": False})
            except Exception:
                pass
            db.commit()
            return {"success": True, "message": "Toda la memoria de recuerdos ha sido borrada."}
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def get_memory_summary(self, mem_type: Optional[str] = None) -> str:
        profile = self.get_all_profile()
        mems = self.recall_memories(limit=50)
        if not mems and not profile:
            return "No tengo recuerdos guardados en este momento."

        mem_map = {m["key"].lower(): m["value"] for m in mems}

        full_name = profile.get("full_name") or mem_map.get("nombre_completo") or profile.get("name") or "Jhonatan David Torres Patiño"
        alias = profile.get("alias") or mem_map.get("alias") or "(Por definir)"
        birthdate = mem_map.get("fecha_nacimiento") or profile.get("birthdate") or "08 / 08 / 2004"
        age = profile.get("age") or mem_map.get("edad") or "22 años"
        age_str = f"{age}" if "año" in str(age) else f"{age} años"

        hobby = mem_map.get("hobby") or profile.get("hobby") or "Programación en Python"
        color = mem_map.get("color_favorito") or profile.get("color") or "Azul oscuro"
        schedule = mem_map.get("horario_universitario") or mem_map.get("horarios_universidad") or profile.get("university_schedule") or "Lunes a Viernes | 18:00 - 22:00"

        genres = mem_map.get("gusto_musical") or profile.get("music_taste") or "Rock, Metal alternativo, Post-punk, Hard rock clásico"
        main_band = mem_map.get("banda_principal") or mem_map.get("banda_favorita") or "Queen"
        featured_bands = mem_map.get("bandas_destacadas") or mem_map.get("bandas_favoritas") or "My Chemical Romance, System of a Down, Scorpions, Audioslave, Avenged Sevenfold"
        if isinstance(featured_bands, list):
            featured_bands = ", ".join(featured_bands)
        elif isinstance(featured_bands, str) and featured_bands.startswith("["):
            try:
                featured_bands = ", ".join(json.loads(featured_bands))
            except Exception:
                pass

        summary_lines = [
            "### IDENTIDAD",
            f"- **Nombre:** {full_name}",
            f"- **Usuario:** {alias}",
            f"- **Nacimiento:** {birthdate} ({age_str})",
            "",
            "### PERFIL & RUTINA",
            f"- **Hobby:** {hobby}",
            f"- **Color:** {color}",
            f"- **Horario Universitario:** {schedule}",
            "",
            "### PREFERENCIAS MUSICALES",
            f"- **Géneros:** {genres}",
            f"- **Banda Principal:** {main_band}",
            f"- **Bandas Destacadas:** {featured_bands}"
        ]

        return "\n".join(summary_lines)

    def export_memory(self) -> Dict[str, Any]:
        mems = self.recall_memories(limit=100)
        profile = self.get_all_profile()
        tasks = self.list_tasks(include_completed=False)
        reminders = self.list_reminders(include_completed=False)
        return {
            "user_profile": profile,
            "memories": mems,
            "active_tasks_count": len(tasks),
            "active_reminders_count": len(reminders),
            "export_timestamp": datetime.now(timezone.utc).isoformat()
        }

    # --- TAREAS ---
    def create_task(self, title: str, description: str = "", priority: str = "NORMAL", project: str = "General") -> Dict[str, Any]:
        db = SessionLocal()
        clean_title = title.strip()
        clean_proj = (project or "General").strip()
        try:
            # Deduplicación de tareas idénticas en ventana de 2 minutos (evitar doble clic / spam)
            recent_threshold = datetime.now(timezone.utc) - timedelta(minutes=2)
            existing = db.query(TaskModel).filter(
                TaskModel.title.ilike(clean_title),
                TaskModel.project.ilike(clean_proj),
                TaskModel.status == "PENDING",
                TaskModel.created_at >= recent_threshold
            ).first()
            if existing:
                return {
                    "success": True, 
                    "data": {
                        "id": existing.id, 
                        "title": existing.title, 
                        "priority": existing.priority, 
                        "project": existing.project, 
                        "status": existing.status
                    }
                }

            task = TaskModel(title=clean_title, description=description, priority=priority, project=clean_proj, status="PENDING")
            db.add(task)
            db.commit()
            db.refresh(task)
            return {"success": True, "data": {"id": task.id, "title": task.title, "priority": task.priority, "project": task.project, "status": task.status}}
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def list_tasks(self, include_completed: bool = False, project: Optional[str] = None) -> List[Dict[str, Any]]:
        db = SessionLocal()
        try:
            q = db.query(TaskModel)
            if not include_completed:
                q = q.filter(TaskModel.status != "COMPLETED")
            if project:
                q = q.filter(TaskModel.project == project)
            rows = q.order_by(TaskModel.id.desc()).all()
            return [{"id": r.id, "title": r.title, "description": r.description, "project": r.project, "priority": r.priority, "status": r.status} for r in rows]
        finally:
            db.close()

    def complete_task(self, task_id: int) -> bool:
        db = SessionLocal()
        try:
            t = db.query(TaskModel).filter(TaskModel.id == task_id).first()
            if t:
                t.status = "COMPLETED"
                t.updated_at = datetime.now(timezone.utc)
                db.commit()
                return True
            return False
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()

    def clear_all_tasks(self) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            deleted = db.query(TaskModel).delete()
            db.commit()
            return {"success": True, "message": f"Se eliminaron {deleted} tareas."}
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    # --- RECORDATORIOS ---
    def create_reminder(
        self, 
        title: str, 
        remind_at_expression: str, 
        priority: str = "NORMAL",
        description: str = ""
    ) -> Dict[str, Any]:
        parsed = TimeParser.parse(remind_at_expression)
        if not parsed.get("success"):
            fallback_dt = datetime.now().astimezone() + timedelta(hours=1)
            target_iso = fallback_dt.isoformat()
            display_dt = f"En 1 hora ({fallback_dt.strftime('%I:%M %p')})"
        else:
            target_iso = parsed["datetime_iso"]
            display_dt = parsed["datetime_formatted"]

        prio_clean = priority.upper() if priority and priority.upper() in ["LOW", "NORMAL", "HIGH", "URGENT"] else "NORMAL"
        clean_title = title.strip()

        db = SessionLocal()
        try:
            # Deduplicación compuesta exacta: (title_normalizado, target_datetime_iso)
            existing = db.query(ReminderModel).filter(
                ReminderModel.title.ilike(clean_title),
                ReminderModel.target_datetime_iso == target_iso,
                ReminderModel.status == "PENDING"
            ).first()
            if existing:
                return {
                    "success": True,
                    "data": {
                        "id": existing.id,
                        "title": existing.title,
                        "target_datetime_iso": existing.target_datetime_iso,
                        "display_datetime": existing.display_datetime,
                        "priority": existing.priority,
                        "status": existing.status,
                        "is_ambiguous": False
                    }
                }

            rem = ReminderModel(
                title=clean_title,
                description=description,
                target_datetime_iso=target_iso,
                display_datetime=display_dt,
                timezone=parsed.get("timezone", "Local"),
                priority=prio_clean,
                status="PENDING",
                stages_notified="",
                is_recurring=parsed.get("is_recurring", False),
                recurrence_rule=parsed.get("recurrence_rule")
            )
            db.add(rem)
            db.commit()
            db.refresh(rem)

            # Sincronización proactiva con APScheduler
            try:
                from core.reminders import reminder_engine
                reminder_engine.sync_job_for_reminder(rem)
            except Exception as e_sched:
                logger.debug(f"[Memoria] No se pudo sincronizar APScheduler: {e_sched}")

            return {
                "success": True,
                "data": {
                    "id": rem.id,
                    "title": rem.title,
                    "target_datetime_iso": rem.target_datetime_iso,
                    "display_datetime": rem.display_datetime,
                    "priority": rem.priority,
                    "status": rem.status,
                    "is_ambiguous": parsed.get("is_ambiguous", False),
                    "is_recurring": rem.is_recurring,
                    "recurrence_rule": rem.recurrence_rule
                }
            }
        except Exception as e:
            db.rollback()
            logger.error(f"[Memoria] Error creando recordatorio: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def list_reminders(self, status_filter: Optional[str] = None, include_completed: bool = False) -> List[Dict[str, Any]]:
        db = SessionLocal()
        try:
            q = db.query(ReminderModel)
            if status_filter:
                q = q.filter(ReminderModel.status == status_filter)
            elif not include_completed:
                q = q.filter(ReminderModel.status.in_(["PENDING", "SNOOZED", "NOTIFIED"]))
            rows = q.order_by(ReminderModel.id.desc()).all()
            return [
                {
                    "id": r.id,
                    "title": r.title,
                    "description": r.description,
                    "target_datetime_iso": r.target_datetime_iso,
                    "display_datetime": r.display_datetime,
                    "priority": r.priority,
                    "status": r.status
                }
                for r in rows
            ]
        finally:
            db.close()

    def snooze_reminder(self, reminder_id: int, minutes: int = 10) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            rem = db.query(ReminderModel).filter(ReminderModel.id == reminder_id).first()
            if not rem:
                return {"success": False, "error": f"No se encontró recordatorio #{reminder_id}"}

            new_target = datetime.now().astimezone() + timedelta(minutes=minutes)
            rem.target_datetime_iso = new_target.isoformat()
            rem.display_datetime = f"Pospuesto a las {new_target.strftime('%I:%M %p')}"
            rem.status = "SNOOZED"
            rem.stages_notified = ""
            rem.updated_at = datetime.now(timezone.utc)
            db.commit()

            # Sincronizar nuevo tiempo con APScheduler
            try:
                from core.reminders import reminder_engine
                reminder_engine.sync_job_for_reminder(rem)
            except Exception:
                pass

            return {
                "success": True,
                "data": {
                    "id": rem.id,
                    "title": rem.title,
                    "new_time": rem.display_datetime,
                    "status": rem.status
                }
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def complete_reminder(self, reminder_id: int) -> bool:
        db = SessionLocal()
        try:
            rem = db.query(ReminderModel).filter(ReminderModel.id == reminder_id).first()
            if rem:
                rem.status = "COMPLETED"
                rem.updated_at = datetime.now(timezone.utc)
                db.commit()
                try:
                    from core.reminders import reminder_engine
                    reminder_engine.remove_job_for_reminder(reminder_id)
                except Exception:
                    pass
                return True
            return False
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()

    def clear_all_reminders(self) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            deleted = db.query(ReminderModel).delete()
            db.commit()
            try:
                from core.reminders import reminder_engine
                reminder_engine.clear_all_jobs()
            except Exception:
                pass
            return {"success": True, "message": f"Se eliminaron {deleted} recordatorios."}
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def delete_reminder(self, reminder_id_or_title: Any) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            rem = None
            if isinstance(reminder_id_or_title, int) or (isinstance(reminder_id_or_title, str) and reminder_id_or_title.isdigit()):
                rem = db.query(ReminderModel).filter(ReminderModel.id == int(reminder_id_or_title)).first()
            elif isinstance(reminder_id_or_title, str):
                rem = db.query(ReminderModel).filter(ReminderModel.title.ilike(f"%{reminder_id_or_title}%")).first()

            if rem:
                title = rem.title
                rem_id = rem.id
                db.delete(rem)
                db.commit()
                try:
                    from core.reminders import reminder_engine
                    reminder_engine.remove_job_for_reminder(rem_id)
                except Exception:
                    pass
                return {"success": True, "message": f"Recordatorio '{title}' eliminado."}
            return {"success": False, "error": f"No se encontró ningún recordatorio que coincida con '{reminder_id_or_title}'."}
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def delete_task(self, task_id_or_title: Any) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            task = None
            if isinstance(task_id_or_title, int) or (isinstance(task_id_or_title, str) and task_id_or_title.isdigit()):
                task = db.query(TaskModel).filter(TaskModel.id == int(task_id_or_title)).first()
            elif isinstance(task_id_or_title, str):
                task = db.query(TaskModel).filter(TaskModel.title.ilike(f"%{task_id_or_title}%")).first()

            if task:
                title = task.title
                db.delete(task)
                db.commit()
                return {"success": True, "message": f"Tarea '{title}' eliminada."}
            return {"success": False, "error": f"No se encontró ninguna tarea que coincida con '{task_id_or_title}'."}
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def clear_all_pending(self) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            del_rems = db.query(ReminderModel).delete()
            del_tasks = db.query(TaskModel).delete()
            db.commit()
            try:
                from core.reminders import reminder_engine
                reminder_engine.clear_all_jobs()
            except Exception:
                pass
            return {
                "success": True,
                "deleted_reminders": del_rems,
                "deleted_tasks": del_tasks,
                "message": f"Se eliminaron todos los pendientes ({del_rems} recordatorios y {del_tasks} tareas)."
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def get_pending_summary(self) -> Dict[str, Any]:
        tasks = self.list_tasks(include_completed=False)
        rems = self.list_reminders(include_completed=False)
        
        summary_lines = []
        if rems:
            rem_items = [f"Recordatorio #{r['id']}: {r['title']} ({r.get('display_datetime', 'Pronto')})" for r in rems[:4]]
            summary_lines.append("Recordatorios: " + "; ".join(rem_items))
        if tasks:
            task_items = [f"Tarea #{t['id']}: {t['title']}" for t in tasks[:4]]
            summary_lines.append("Tareas: " + "; ".join(task_items))
            
        if not summary_lines:
            text = "No tienes tareas ni recordatorios pendientes."
        else:
            text = " | ".join(summary_lines)

        return {
            "reminders": rems,
            "tasks": tasks,
            "total_pending": len(tasks) + len(rems),
            "summary_text": text
        }

memory_manager = MemoryManager()
