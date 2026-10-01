from datetime import datetime
from typing import Dict, Any, Optional
from core.config import settings
from core.location_provider import LocationProvider
from core.system_capabilities import SystemCapabilities

class ContextEngine:
    """
    Provee contexto dinámico espacio-temporal y percepción ambiental en tiempo real.
    Garantiza que JARVIS nunca tenga que 'adivinar' hora, fecha, lugar o estado del PC.
    """
    
    DAYS_ES = {
        0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
        4: "viernes", 5: "sábado", 6: "domingo"
    }
    
    MONTHS_ES = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }

    @classmethod
    def get_system_timezone_str(cls) -> str:
        if settings.TIMEZONE_OVERRIDE:
            return settings.TIMEZONE_OVERRIDE
        try:
            now = datetime.now().astimezone()
            tz_info = now.tzinfo
            return str(tz_info) or "Local Timezone"
        except Exception:
            return "Local Timezone"

    @classmethod
    def get_current_datetime_dict(cls) -> Dict[str, Any]:
        now = datetime.now().astimezone()
        weekday_name = cls.DAYS_ES.get(now.weekday(), "")
        month_name = cls.MONTHS_ES.get(now.month, "")
        
        time_12h = now.strftime("%I:%M %p").lstrip("0")
        time_24h = now.strftime("%H:%M:%S")
        formatted_date = f"{weekday_name}, {now.day} de {month_name} de {now.year}"
        
        utc_offset_str = now.strftime("%z")
        if len(utc_offset_str) == 5:
            utc_offset = f"{utc_offset_str[:3]}:{utc_offset_str[3:]}"
        else:
            utc_offset = "+00:00"

        return {
            "iso": now.isoformat(),
            "date": formatted_date,
            "time_12h": time_12h,
            "time_24h": time_24h,
            "day_of_week": weekday_name,
            "day": now.day,
            "month": now.month,
            "year": now.year,
            "timezone": cls.get_system_timezone_str(),
            "utc_offset": utc_offset,
            "timestamp": int(now.timestamp())
        }

    @classmethod
    def build_system_context_block(
        cls, 
        user_profile: Optional[Dict[str, Any]] = None, 
        recent_memories: Optional[list] = None, 
        pending_tasks_count: int = 0,
        active_reminders_count: int = 0
    ) -> str:
        dt = cls.get_current_datetime_dict()
        loc = LocationProvider.get_location()
        env = SystemCapabilities.get_full_environmental_status()
        
        lines = [
            "=== JARVIS CONTEXT (PERCEPCIÓN AMBIENTAL EN TIEMPO REAL) ===",
            f"- Fecha: {dt['date']}",
            f"- Hora actual: {dt['time_12h']} ({dt['time_24h']})",
            f"- Zona horaria: {dt['timezone']} (UTC {dt['utc_offset']})",
            f"- Día de la semana: {dt['day_of_week']}"
        ]
        
        # Ubicación real
        if loc.get("available") and loc.get("city"):
            loc_str = f"{loc['city']}, {loc.get('country', '')}"
            lines.append(f"- Ubicación: {loc_str} (Fuente: {loc.get('source')})")
        elif loc.get("status") == "disabled":
            lines.append("- Ubicación: Desactivada por privacidad")
        else:
            lines.append("- Ubicación: No disponible")

        # Percepción del Sistema y Escritorio
        lines.append(f"- Sistema: {env['os']}")
        lines.append(f"- Conectividad: {env['connectivity']}")
        lines.append(f"- Micrófono: {env['microphone']}")
        lines.append(f"- Notificaciones: {env['notifications']}")
        
        if env.get("active_app") and env["active_app"] != "Desconocido":
            lines.append(f"- Aplicación activa: {env['active_app']}")
            if env.get("active_window") and env["active_window"] != env["active_app"]:
                lines.append(f"- Ventana activa: {env['active_window']}")

        # Pendientes y Tareas
        if pending_tasks_count > 0:
            lines.append(f"- Tareas pendientes activas: {pending_tasks_count}")
        if active_reminders_count > 0:
            lines.append(f"- Recordatorios activos supervisados: {active_reminders_count}")
            
        # --- PERFIL DEL USUARIO (PERSISTENTE, SIEMPRE PRESENTE) ---
        if user_profile:
            lines.append("")
            lines.append("=== PERFIL DEL USUARIO (MEMORIA PERMANENTE) ===")

            name = user_profile.get("full_name") or user_profile.get("name") or "el usuario"
            lines.append(f"- Nombre completo: {name}")

            # Alias/apodo: si existe, indicar explícitamente cómo dirigirse al usuario
            alias = user_profile.get("alias") or user_profile.get("apodo") or user_profile.get("nickname") or user_profile.get("me_llaman")
            if alias:
                lines.append(f"- Alias/Apodo (cómo prefiere que le llamen): {alias}")
                lines.append(f"  → SIEMPRE llámale '{alias}' en la conversación, no por su nombre completo.")

            age = user_profile.get("age")
            if age:
                lines.append(f"- Edad: {age} años")

            birthdate = user_profile.get("birthdate")
            if birthdate:
                lines.append(f"- Fecha de nacimiento: {birthdate}")

            music_taste = user_profile.get("music_taste")
            if music_taste:
                lines.append(f"- Gusto musical: {music_taste}")

            bands = user_profile.get("favorite_bands")
            if bands:
                import json
                if isinstance(bands, str):
                    try:
                        bands = json.loads(bands)
                    except Exception:
                        pass
                if isinstance(bands, list):
                    bands_str = ", ".join(bands)
                else:
                    bands_str = str(bands)
                lines.append(f"- Bandas favoritas: {bands_str}")

            # Campos genéricos adicionales
            skip_keys = {"name", "full_name", "age", "birthdate", "music_taste", "favorite_bands", "preferred_music", "user_name"}
            for k, v in user_profile.items():
                if k not in skip_keys and v:
                    val_str = str(v) if not isinstance(v, list) else ", ".join(str(x) for x in v)
                    lines.append(f"- {k.replace('_', ' ').capitalize()}: {val_str}")

            lines.append("============================================================")

        # Recuerdos recientes relevantes
        if recent_memories:
            lines.append("- Recuerdos relevantes del usuario:")
            for m in recent_memories[-5:]:
                lines.append(f"  * {m.get('key')}: {m.get('value')}")
                
        lines.append("============================================================")
        return "\n".join(lines)

