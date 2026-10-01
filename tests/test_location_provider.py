import json
import pytest
import urllib.request
from unittest.mock import MagicMock
from core.location_provider import LocationProvider
from core.config import settings

def test_location_structure(monkeypatch):
    class MockResponse:
        status = 200
        def read(self):
            return json.dumps({
                "city": "Ciudad de México",
                "region": "CDMX",
                "country_name": "México",
                "country_code": "MX",
                "timezone": "America/Mexico_City",
                "latitude": 19.4326,
                "longitude": -99.1332
            }).encode("utf-8")
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=2.0: MockResponse())
    loc = LocationProvider.get_location(force_refresh=True)
    assert isinstance(loc, dict)
    assert loc["status"] == "available"
    assert loc["available"] is True
    assert loc["city"] == "Ciudad de México"
    assert loc["country"] == "México"

def test_location_privacy_disabled(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_LOCATION", False)
    loc = LocationProvider.get_location(force_refresh=True)
    assert loc["status"] == "disabled"
    assert loc["available"] is False
    assert loc["source"] == "privacy_disabled"
