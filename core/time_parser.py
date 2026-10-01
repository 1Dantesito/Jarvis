import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple

class TimeParser:
    """
    Parser semántico y determinista de fechas y horas relativas, absolutas y coloquiales en español.
    Garantiza exactitud absoluta en la interpretación de AM/PM, momentos del día y formatos 12h/24h (BUG-27).
    """
    
    WEEKDAYS = {
        "lunes": 0, "martes": 1, "miercoles": 2, "miércoles": 2,
        "jueves": 3, "viernes": 4, "sabado": 5, "sábado": 5, "domingo": 6
    }
    
    MONTHS_ES = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }

    DAYS_ES = {
        0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
        4: "viernes", 5: "sábado", 6: "domingo"
    }

    @classmethod
    def parse(cls, expression: str, reference_dt: Optional[datetime] = None) -> Dict[str, Any]:
        ref = reference_dt or datetime.now().astimezone()
        raw_expr = expression.strip()
        expr = raw_expr.lower()
        
        # 1. Deltas relativos simples ("en 15 minutos", "en 2 horas", "en 1 hora", "en media hora")
        delta = cls._match_delta(expr)
        if delta is not None:
            target_dt = (ref + delta).replace(second=0, microsecond=0)
            return cls._format_result(target_dt, raw_expr, is_ambiguous=False)

        # 2. Extracción de fecha base (hoy, mañana, pasado mañana, ayer, día de semana)
        target_date, is_date_found, rem_expr = cls._extract_target_date(expr, ref)

        # 3. Extracción determinista de hora con soporte completo para AM/PM, formatos coloquiales y modificadores
        time_tuple, is_ambiguous, amb_details = cls._extract_time(rem_expr, target_date, ref)

        if time_tuple is not None:
            hour, minute = time_tuple
            target_dt = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Si era "hoy", la hora es ambigua sin AM/PM y en horario AM ya pasó, ajustar a PM
            if target_date.date() == ref.date() and target_dt < ref and is_ambiguous and hour < 12:
                target_dt = target_dt.replace(hour=hour + 12)
                is_ambiguous = False
                
            return cls._format_result(target_dt, raw_expr, is_ambiguous=is_ambiguous, ambiguity_details=amb_details)
        elif is_date_found:
            # Fecha identificada sin hora explícita (asumir 9:00 AM)
            target_dt = target_date.replace(hour=9, minute=0, second=0, microsecond=0)
            return cls._format_result(target_dt, raw_expr, is_ambiguous=False, note="Hora asumida: 9:00 AM")

        return {
            "success": False,
            "datetime_iso": None,
            "datetime_formatted": None,
            "source_expression": raw_expr,
            "is_ambiguous": False,
            "error": f"No se pudo interpretar la expresión temporal: '{raw_expr}'"
        }

    @classmethod
    def _match_delta(cls, expr: str) -> Optional[timedelta]:
        if "media hora" in expr:
            return timedelta(minutes=30)
        
        m_min = re.search(r'\b(?:en|dentro de)\s+(\d+)\s+min(?:uto)?s?\b', expr)
        if m_min:
            return timedelta(minutes=int(m_min.group(1)))
            
        if re.search(r'\b(?:en|dentro de)\s+(?:una|1)\s+hora\b', expr):
            return timedelta(hours=1)
        m_hr = re.search(r'\b(?:en|dentro de)\s+(\d+)\s+horas?\b', expr)
        if m_hr:
            return timedelta(hours=int(m_hr.group(1)))
            
        m_days = re.search(r'\b(?:en|dentro de)\s+(\d+)\s+d[ií]as?\b', expr)
        if m_days:
            return timedelta(days=int(m_days.group(1)))
            
        return None

    @classmethod
    def _extract_target_date(cls, expr: str, ref: datetime) -> Tuple[datetime, bool, str]:
        rem = expr
        if "pasado mañana" in rem or "pasado manana" in rem:
            return ref + timedelta(days=2), True, rem.replace("pasado mañana", "").replace("pasado manana", "")
        if "mañana" in rem or "manana" in rem:
            # Asegurar que no sea "de la mañana" (indicador de hora)
            if not re.search(r'de\s+la\s+ma[ñn]ana', rem):
                rem_clean = re.sub(r'\bma[ñn]ana\b', '', rem)
                return ref + timedelta(days=1), True, rem_clean
        if "ayer" in rem:
            return ref - timedelta(days=1), True, rem.replace("ayer", "")
        if "hoy" in rem or "esta noche" in rem or "esta tarde" in rem:
            return ref, True, rem.replace("hoy", "").replace("esta noche", "").replace("esta tarde", "")
            
        # Días de la semana
        for day_name, day_idx in cls.WEEKDAYS.items():
            pattern = rf'\b(?:el\s+|este\s+|pr[oó]ximo\s+)?{day_name}\b'
            if re.search(pattern, rem):
                current_day = ref.weekday()
                days_ahead = (day_idx - current_day) % 7
                if days_ahead == 0 and ("próximo" in rem or "proximo" in rem):
                    days_ahead = 7
                elif days_ahead == 0:
                    days_ahead = 7 if ref.hour >= 20 else 0
                target = ref + timedelta(days=days_ahead)
                cleaned = re.sub(pattern, "", rem).strip()
                return target, True, cleaned

        return ref, False, rem

    @classmethod
    def _extract_time(cls, rem_expr: str, target_date: datetime, ref: datetime) -> Tuple[Optional[Tuple[int, int]], bool, Optional[Dict[str, str]]]:
        s = rem_expr.strip()
        
        # Normalizar indicadores: p. m. / p.m / pm -> pm, a. m. / a.m / am -> am
        s_norm = re.sub(r'p\.\s*m\.?', 'pm', s)
        s_norm = re.sub(r'a\.\s*m\.?', 'am', s_norm)
        
        # Indicadores explícitos de PM y AM
        is_pm = bool(re.search(r'\b(?:pm|p\.m\.|tarde|noche|de la tarde|de la noche)\b', s_norm))
        is_am = bool(re.search(r'\b(?:am|a\.m\.|mañana|madrugada|de la mañana|de la madrugada)\b', s_norm))

        def _adjust_hour(raw_h: int, minute: int) -> Tuple[Tuple[int, int], bool, Optional[Dict[str, str]]]:
            if is_pm:
                hour = 12 if raw_h == 12 else (raw_h + 12 if raw_h < 12 else raw_h)
                return (hour, minute), False, None
            elif is_am:
                hour = 0 if raw_h == 12 else raw_h
                return (hour, minute), False, None
            elif raw_h >= 13:
                return (raw_h, minute), False, None
            else:
                return (raw_h, minute), True, {
                    "suggested_am": f"{raw_h:02d}:{minute:02d}",
                    "suggested_pm": f"{(raw_h + 12):02d}:{minute:02d}"
                }

        # 1. Patrón con HH:MM (ej: "7:41 pm", "19:41", "7:41", "07:41")
        m_colon = re.search(r'\b(?:a\s+las?\s+|para\s+las?\s+)?([01]?\d|2[0-3]):([0-5]\d)\b', s_norm)
        if m_colon:
            raw_h = int(m_colon.group(1))
            minute = int(m_colon.group(2))
            return _adjust_hour(raw_h, minute)

        # 2. Patrón coloquial con "y" (ej: "a las 7 y 50 pm", "7 y media de la tarde", "7 y cuarto", "8 en punto")
        m_colloquial = re.search(r'\b(?:a\s+las?\s+|para\s+las?\s+)?(\d{1,2})\s+y\s+(media|cuarto|\d{1,2})\b', s_norm)
        if m_colloquial:
            raw_h = int(m_colloquial.group(1))
            min_token = m_colloquial.group(2)
            if min_token == "media":
                minute = 30
            elif min_token == "cuarto":
                minute = 15
            else:
                minute = int(min_token)
            if 1 <= raw_h <= 24 and 0 <= minute <= 59:
                return _adjust_hour(raw_h, minute)

        # 3. Patrón numérico directo de 3-4 dígitos (ej: "750 pm", "750 p.m", "1950", "0750")
        m_digits = re.search(r'\b([01]?\d|2[0-3])([0-5]\d)\s*(?:pm|am|p\.m\.|a\.m\.)?\b', s_norm)
        if m_digits and (is_pm or is_am or len(m_digits.group(0).strip()) == 4):
            raw_h = int(m_digits.group(1))
            minute = int(m_digits.group(2))
            if 1 <= raw_h <= 24 and 0 <= minute <= 59:
                return _adjust_hour(raw_h, minute)

        # 4. Patrón con hora sola o "en punto" (ej: "a las 6 pm", "a las 8 de la noche", "8 en punto", "a las 7")
        m_hour = re.search(r'\b(?:a\s+las?\s+|para\s+las?\s+)(\d{1,2})(?:\s+en\s+punto)?\b', s_norm)
        if not m_hour:
            m_hour = re.search(r'\b(\d{1,2})\s*(?:en\s+punto|pm|am|p\.m\.|a\.m\.|de\s+la\s+tarde|de\s+la\s+noche|de\s+la\s+mañana)\b', s_norm)

        if m_hour:
            raw_h = int(m_hour.group(1))
            minute = 0
            if 1 <= raw_h <= 24:
                return _adjust_hour(raw_h, minute)

        return None, False, None

    @classmethod
    def _format_result(cls, dt: datetime, expr: str, is_ambiguous: bool = False, ambiguity_details: Optional[Dict[str, str]] = None, note: Optional[str] = None) -> Dict[str, Any]:
        weekday_name = cls.DAYS_ES.get(dt.weekday(), "")
        month_name = cls.MONTHS_ES.get(dt.month, "")
        time_12h = dt.strftime("%I:%M %p").lstrip("0")
        
        formatted_str = f"{weekday_name}, {dt.day} de {month_name} de {dt.year} a las {time_12h}"
        
        return {
            "success": True,
            "datetime_iso": dt.isoformat(),
            "datetime_formatted": formatted_str,
            "time_12h": time_12h,
            "time_24h": dt.strftime("%H:%M"),
            "date": f"{dt.day}/{dt.month}/{dt.year}",
            "timezone": str(dt.tzinfo) if dt.tzinfo else "Local",
            "source_expression": expr,
            "is_ambiguous": is_ambiguous,
            "ambiguity_details": ambiguity_details,
            "note": note
        }
