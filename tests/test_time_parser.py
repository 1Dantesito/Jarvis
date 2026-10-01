import pytest
from datetime import datetime, timezone, timedelta
from core.time_parser import TimeParser

def test_relative_delta_minutes():
    ref = datetime(2026, 8, 17, 10, 0, 0, tzinfo=timezone.utc)
    res = TimeParser.parse("en 15 minutos", reference_dt=ref)
    assert res["success"] is True
    assert res["time_24h"] == "10:15"

def test_relative_delta_hours():
    ref = datetime(2026, 8, 17, 10, 0, 0, tzinfo=timezone.utc)
    res = TimeParser.parse("en 2 horas", reference_dt=ref)
    assert res["success"] is True
    assert res["time_24h"] == "12:00"

def test_relative_delta_half_hour():
    ref = datetime(2026, 8, 17, 10, 0, 0, tzinfo=timezone.utc)
    res = TimeParser.parse("en media hora", reference_dt=ref)
    assert res["success"] is True
    assert res["time_24h"] == "10:30"

def test_tomorrow_morning_and_afternoon():
    ref = datetime(2026, 8, 17, 10, 0, 0, tzinfo=timezone.utc)
    res_pm = TimeParser.parse("mañana a las 6 pm", reference_dt=ref)
    assert res_pm["success"] is True
    assert res_pm["time_24h"] == "18:00"
    assert "18 de agosto" in res_pm["datetime_formatted"]

    res_tarde = TimeParser.parse("mañana a las 6 de la tarde", reference_dt=ref)
    assert res_tarde["success"] is True
    assert res_tarde["time_24h"] == "18:00"

def test_pasado_manana():
    ref = datetime(2026, 8, 17, 10, 0, 0, tzinfo=timezone.utc)
    res = TimeParser.parse("pasado mañana a las 11:30", reference_dt=ref)
    assert res["success"] is True
    assert res["time_24h"] == "11:30"
    assert "19 de agosto" in res["datetime_formatted"]

def test_ayer():
    ref = datetime(2026, 8, 17, 10, 0, 0, tzinfo=timezone.utc)
    res = TimeParser.parse("ayer a las 3 pm", reference_dt=ref)
    assert res["success"] is True
    assert "16 de agosto" in res["datetime_formatted"]
    assert res["time_24h"] == "15:00"

def test_weekdays_parsing():
    # Lunes 17 de agosto de 2026
    ref = datetime(2026, 8, 17, 10, 0, 0, tzinfo=timezone.utc)
    res_viernes = TimeParser.parse("este viernes a las 4 pm", reference_dt=ref)
    assert res_viernes["success"] is True
    assert "viernes" in res_viernes["datetime_formatted"]
    assert "21 de agosto" in res_viernes["datetime_formatted"]
    assert res_viernes["time_24h"] == "16:00"

def test_ambiguity_detection():
    ref = datetime(2026, 8, 17, 10, 0, 0, tzinfo=timezone.utc)
    res = TimeParser.parse("mañana a las 6", reference_dt=ref)
    assert res["success"] is True
    assert res["is_ambiguous"] is True
    assert res["ambiguity_details"]["suggested_am"] == "06:00"
    assert res["ambiguity_details"]["suggested_pm"] == "18:00"
