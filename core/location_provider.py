import time
import json
import urllib.request
from typing import Dict, Any, Optional
from core.config import settings
from core.logger import logger

class LocationProvider:
    """
    Proveedor de ubicación no invasivo con caché y respeto a políticas de privacidad.
    """
    _cache: Optional[Dict[str, Any]] = None
    _cache_time: float = 0.0
    CACHE_DURATION: float = 3600.0  # 1 hora

    @classmethod
    def is_enabled(cls) -> bool:
        return settings.ENABLE_LOCATION

    @classmethod
    def get_cached_country_code(cls) -> Optional[str]:
        """
        Retorna el código ISO del país (ej. 'CO', 'ES', 'MX', 'US') si existe en caché de memoria (RAM).
        Garantiza tiempo de respuesta cero (<0.1 ms) sin realizar llamadas HTTP ni bloqueos de red.
        """
        if cls._cache and isinstance(cls._cache, dict):
            return cls._cache.get("country_code")
        return None

    @classmethod
    def get_location(cls, force_refresh: bool = False) -> Dict[str, Any]:
        if not cls.is_enabled():
            return {
                "status": "disabled",
                "message": "Ubicación desactivada por configuración de privacidad.",
                "available": False,
                "city": None,
                "region": None,
                "country": None,
                "timezone": None,
                "coordinates": None,
                "source": "privacy_disabled"
            }

        now = time.time()
        if not force_refresh and cls._cache and (now - cls._cache_time) < cls.CACHE_DURATION:
            return cls._cache

        # 1. Intentar ipapi.co con timeout corto
        try:
            req = urllib.request.Request(
                "https://ipapi.co/json/",
                headers={"User-Agent": "JARVIS-Assistant/2.0"}
            )
            with urllib.request.urlopen(req, timeout=2.0) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    res = {
                        "status": "available",
                        "available": True,
                        "city": data.get("city"),
                        "region": data.get("region"),
                        "country": data.get("country_name"),
                        "country_code": data.get("country_code"),
                        "timezone": data.get("timezone"),
                        "coordinates": {
                            "latitude": data.get("latitude"),
                            "longitude": data.get("longitude")
                        } if settings.ALLOW_EXACT_COORDINATES else None,
                        "source": "ip_geolocation",
                        "updated_at": int(now)
                    }
                    cls._cache = res
                    cls._cache_time = now
                    return res
        except Exception as e:
            logger.debug(f"[LocationProvider] Intento primario ipapi falló ({e}).")

        # 2. Fallback ip-api.com
        try:
            req = urllib.request.Request(
                "http://ip-api.com/json/",
                headers={"User-Agent": "JARVIS-Assistant/2.0"}
            )
            with urllib.request.urlopen(req, timeout=2.0) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    if data.get("status") == "success":
                        res = {
                            "status": "available",
                            "available": True,
                            "city": data.get("city"),
                            "region": data.get("regionName"),
                            "country": data.get("country"),
                            "country_code": data.get("countryCode"),
                            "timezone": data.get("timezone"),
                            "coordinates": {
                                "latitude": data.get("lat"),
                                "longitude": data.get("lon")
                            } if settings.ALLOW_EXACT_COORDINATES else None,
                            "source": "ip_geolocation_fallback",
                            "updated_at": int(now)
                        }
                        cls._cache = res
                        cls._cache_time = now
                        return res
        except Exception as e:
            logger.debug(f"[LocationProvider] Fallback ip-api falló ({e}).")

        # 3. Estado estructurado no disponible (sin inventar)
        return {
            "status": "unavailable",
            "message": "Servicio de ubicación no disponible temporalmente.",
            "available": False,
            "city": None,
            "region": None,
            "country": None,
            "timezone": None,
            "coordinates": None,
            "source": "unavailable"
        }
