import random
import re
from typing import Dict, Any, Optional
from core.user_profile import PersonalityProfile

class ConversationState:
    CASUAL = "CASUAL"
    PRODUCTIVE = "PRODUCTIVE"
    TECHNICAL = "TECHNICAL"
    SERIOUS = "SERIOUS"
    ENTERTAINMENT = "ENTERTAINMENT"
    EMPATHETIC = "EMPATHETIC"
    URGENT = "URGENT"
    FEEDBACK = "FEEDBACK"

class SocialResponseLayer:
    """
    Capa de Expresión Social y Naturalidad Conversacional para JARVIS v3.0.
    Garantiza respuestas humanas, fluidas y sin lenguaje técnico ni confirmaciones genéricas vacías (BUG-24).
    """

    @classmethod
    def detect_state(cls, user_text: str) -> str:
        low = user_text.lower().strip()
        
        # Feedback de estilo
        if any(w in low for w in ["más corto", "mas corto", "más divertido", "mas divertido", "deja de hacer bromas", "más serio", "mas serio", "muy robótico", "muy robotico", "más natural", "mas natural", "eso estuvo bien", "me gustó esa respuesta"]):
            return ConversationState.FEEDBACK
            
        # Empatía
        if any(w in low for w in ["estoy cansado", "tuve un mal día", "estoy agotado", "me siento mal", "estoy estresado"]):
            return ConversationState.EMPATHETIC
            
        # Urgente
        if any(w in low for w in ["urgente", "en 5 minutos", "apúrate", "rápido", "tengo una reunión en", "vuelo"]):
            return ConversationState.URGENT

        # Productividad
        if any(w in low for w in ["organízame el día", "organizame el dia", "qué tengo pendiente", "que tengo pendiente", "mis tareas", "recordatorios", "tengo algún recordatorio"]):
            return ConversationState.PRODUCTIVE
            
        # Entretenimiento (música, vídeos, canciones)
        if any(w in low for w in ["pon", "música", "musica", "cancion", "canción", "algo bueno", "algo triste", "algo pesado", "recomienda", "spotify"]):
            return ConversationState.ENTERTAINMENT
            
        # Casual
        if any(w in low for w in ["hola jarvis", "hola", "qué haces", "que haces", "cómo estás", "como estas"]):
            return ConversationState.CASUAL

        return ConversationState.CASUAL

    @classmethod
    def format_social_tool_phrase(
        cls, 
        tool_name: str, 
        tool_args: Dict[str, Any], 
        tool_result: Dict[str, Any], 
        personality: PersonalityProfile
    ) -> str:
        """
        Formatea el resultado de una herramienta de manera natural, humana y contextual.
        Distingue estrictamente entre acciones (mutaciones de estado) y consultas (lecturas de datos) (BUG-24).
        """
        # 1. Manejo explícito de fallos
        if not tool_result.get("success"):
            err = tool_result.get("error") or "No pude realizar la acción solicitada."
            return f"Hubo un problema: {err}" if personality.humor > 1 else f"No pude completar la solicitud: {err}"

        data = tool_result.get("data", {})

        # =========================================================================
        # 2. HERRAMIENTAS DE CONSULTA (QUERY) — Redacción rica y natural
        # =========================================================================
        if tool_name == "list_reminders":
            rems = data.get("reminders", [])
            total = len(rems)
            if total == 0:
                return "No tienes recordatorios pendientes por ahora."
            elif total <= 3:
                r_titles = ", ".join([f"'{r.get('title')}'" for r in rems if r.get('title')])
                return f"Tienes {total} recordatorio{'s' if total > 1 else ''}: {r_titles}."
            else:
                r_titles = ", ".join([f"'{r.get('title')}'" for r in rems[:3] if r.get('title')])
                rem_count = total - 3
                return f"Tienes {total} recordatorios pendientes; los 3 más próximos son {r_titles}, y {rem_count} más."

        elif tool_name == "list_tasks":
            tasks = data.get("tasks", [])
            total = len(tasks)
            if total == 0:
                return "No tienes tareas pendientes por ahora."
            elif total <= 3:
                t_str = ", ".join([f"'{t['title']}'" for t in tasks if t.get('title')])
                return f"Tus pendientes activos son: {t_str}."
            else:
                t_str = ", ".join([f"'{t['title']}'" for t in tasks[:3] if t.get('title')])
                rem_count = total - 3
                return f"Tienes {total} tareas pendientes; las principales son {t_str}, y {rem_count} más."

        elif tool_name == "get_pending_summary":
            rems = data.get("reminders", [])
            tasks = data.get("tasks", [])
            if not rems and not tasks:
                return "No tienes tareas ni recordatorios pendientes."
            parts = []
            if rems:
                total_r = len(rems)
                if total_r <= 3:
                    r_titles = ", ".join([f"'{r.get('title', '')}'" for r in rems if r.get("title")])
                    parts.append(f"Tienes {total_r} recordatorio{'s' if total_r > 1 else ''}: {r_titles}")
                else:
                    r_titles = ", ".join([f"'{r.get('title', '')}'" for r in rems[:3] if r.get("title")])
                    parts.append(f"Tienes {total_r} recordatorios (los 3 más próximos: {r_titles}, y {total_r - 3} más)")
            if tasks:
                total_t = len(tasks)
                if total_t <= 3:
                    t_titles = ", ".join([f"'{t.get('title', '')}'" for t in tasks if t.get("title")])
                    parts.append(f"{total_t} tarea{'s' if total_t > 1 else ''}: {t_titles}")
                else:
                    t_titles = ", ".join([f"'{t.get('title', '')}'" for t in tasks[:3] if t.get("title")])
                    parts.append(f"{total_t} tareas (principales: {t_titles}, y {total_t - 3} más)")
            return ". ".join(parts) + "."

        elif tool_name in ["current_datetime", "get_current_datetime"]:
            t_str = data.get("time_12h") or data.get("time", "")
            d_str = data.get("date_formatted") or data.get("date", "")
            if t_str and d_str:
                return f"Hoy es {d_str} y son las {t_str}."
            elif t_str:
                return f"Son las {t_str}."
            return f"Fecha y hora actual consultadas."

        elif tool_name == "get_location":
            if data.get("available") and data.get("city"):
                return f"Estás en {data.get('city')}, {data.get('country')}."
            return "No tengo acceso a tu ubicación en este momento."

        elif tool_name == "get_running_applications":
            apps = data.get("running_apps", [])
            if apps:
                app_list = ", ".join(apps[:5])
                return f"Tienes abiertas las siguientes aplicaciones: {app_list}."
            return "No detecté aplicaciones principales en ejecución."

        elif tool_name == "get_active_application":
            app = data.get("application") or data.get("name", "")
            if app:
                return f"La aplicación activa en primer plano es {app}."
            return "No pude determinar la aplicación en primer plano."

        elif tool_name == "search_files":
            matches = data.get("matches", [])
            if matches:
                f_names = ", ".join([m.get("name", "") for m in matches[:3]])
                return f"Encontré {len(matches)} archivo{'s' if len(matches)>1 else ''}: {f_names}."
            return data.get("message", "No encontré ningún archivo que coincida con esa búsqueda.")

        elif tool_name == "read_text_file":
            fn = tool_args.get("file_path", "archivo")
            cnt = data.get("content", "")
            if cnt:
                snippet = cnt[:180] + ("..." if len(cnt) > 180 else "")
                return f"El archivo dice: {snippet}"
            return f"El archivo {fn} está vacío."

        elif tool_name == "recall_memories":
            summary = data.get("summary", "")
            if summary and "No tengo recuerdos" not in summary:
                return summary
            mems = data.get("memories", [])
            if mems:
                frases = []
                for m in mems:
                    k = str(m.get("key", "")).lower()
                    v = str(m.get("value", "")).strip()
                    if any(nk in k for nk in ["nombre", "name", "usuario"]):
                        frases.append(f"te llamas {v}")
                    elif v:
                        frases.append(f"{k}: {v}")
                return f"Recuerdo que {', '.join(frases)}."
            return "No tengo ningún recuerdo guardado sobre ese tema."

        elif tool_name == "get_memory_summary":
            return data.get("summary", "Consulta de memoria completada.")

        elif tool_name == "get_now_playing":
            track = data.get("current_track", {})
            if track and track.get("title"):
                return f"Está sonando '{track.get('title')}' de {track.get('artist', 'Artista')}."
            return "No hay ninguna canción reproduciéndose en este momento."

        elif tool_name == "get_music_queue":
            q = data.get("queue", [])
            if q:
                return f"Hay {len(q)} canciones en la cola de reproducción."
            return "La cola de reproducción está vacía."

        elif tool_name == "recommend_music":
            exp = data.get("explanation", "")
            if exp:
                return f"Tengo una selección: {exp}"
            return "Preparé unas recomendaciones de música para ti."

        elif tool_name == "web_search":
            results = data.get("results", [])
            if results:
                top = results[0]
                return f"Según mi búsqueda: {top.get('snippet', top.get('title', ''))}"
            return "No encontré resultados relevantes para esa búsqueda."

        elif tool_name == "ping":
            return "Conexión activa y funcionando normalmente."

        # =========================================================================
        # 3. HERRAMIENTAS DE ACCIÓN (ACTION) — Confirmaciones humanas y específicas
        # =========================================================================
        elif tool_name == "create_reminder":
            time_str = data.get("display_datetime") or tool_args.get("remind_at") or "más tarde"
            title = tool_args.get("title", "")
            if title:
                return f"Listo, te avisaré de {title} {time_str}."
            return f"Listo, te avisaré {time_str}."

        elif tool_name == "snooze_reminder":
            mins = tool_args.get("minutes", 10)
            return f"Recordatorio pospuesto {mins} minutos."

        elif tool_name == "complete_reminder":
            return "Recordatorio completado."

        elif tool_name == "delete_reminder":
            return "Recordatorio eliminado."

        elif tool_name == "clear_all_reminders":
            return "Todos tus recordatorios han sido eliminados."

        elif tool_name == "clear_all_pending":
            return "He eliminado todas tus tareas y recordatorios pendientes."

        elif tool_name == "create_task":
            return f"Tarea agregada: '{tool_args.get('title')}'."

        elif tool_name == "complete_task":
            return "Tarea completada."

        elif tool_name == "delete_task":
            return "Tarea eliminada."

        elif tool_name == "clear_all_tasks":
            return "Todas tus tareas han sido eliminadas."

        elif tool_name == "open_application":
            app = data.get("app") or tool_args.get("app_name", "la aplicación")
            variations = [f"Abriendo {app}.", f"Listo, abriendo {app}."]
            return random.choice(variations)

        elif tool_name == "focus_application":
            app = data.get("app") or tool_args.get("app_name", "la aplicación")
            return f"Cambiando a {app}."

        elif tool_name == "close_application":
            app = data.get("app") or tool_args.get("app_name", "la aplicación")
            variations = [f"Cerrando {app}.", f"Listo, cerré {app}."]
            return random.choice(variations)

        elif tool_name == "create_text_file":
            fn = tool_args.get("filename", "archivo")
            return f"Listo, he creado el archivo {fn} en tu Escritorio."

        elif tool_name == "open_url":
            return f"Abriendo enlace en tu navegador."

        elif tool_name == "play_music":
            track = data.get("current_track", {})
            if track:
                return f"Reproduciendo '{track.get('title')}' de {track.get('artist')}."
            return "Iniciando reproducción musical."

        elif tool_name == "pause_music":
            return "Música pausada."

        elif tool_name == "resume_music":
            return "Reanudando la música."

        elif tool_name == "skip_music":
            nxt = data.get("next_track", {})
            if nxt:
                return f"Siguiente: '{nxt.get('title')}' de {nxt.get('artist')}."
            return "Pasando a la siguiente canción."

        elif tool_name == "clear_music_queue":
            return "Cola de reproducción vaciada."

        elif tool_name == "remember_info":
            k = str(tool_args.get("key", "")).strip().lower()
            v = str(tool_args.get("value", "")).strip()
            if any(nk in k for nk in ["nombre", "name", "usuario", "user"]):
                nombre_val = v or tool_args.get("key", "")
                return f"Mucho gusto, {nombre_val}. Ya lo he guardado en mi memoria."
            elif "cumple" in k:
                return f"Anotado, recordaré la fecha de tu cumpleaños: {v}."
            elif "gusta" in k or "favorit" in k:
                return f"Perfecto, ya sé que te gusta {v}."
            elif v:
                return f"Entendido, recordaré que {v}."
            return "Entendido, lo he guardado en mi memoria."

        elif tool_name == "forget_memory":
            count = data.get("forgotten_count", 0)
            if count > 0:
                return "Listo, he eliminado ese recuerdo de mi memoria."
            return "No encontré ningún recuerdo registrado sobre ese tema para olvidar."

        elif tool_name == "clear_memory":
            return "Toda tu memoria de recuerdos ha sido borrada."

        return "Acción completada."
