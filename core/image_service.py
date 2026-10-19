"""
core/image_service.py - Servicio de búsqueda y resolución de imágenes reales para listas y tarjetas showcase.
Proporciona resolución asíncrona de fotografías e ilustraciones legítimas desde Wikimedia Commons,
Wikipedia API y Bing Images con almacenamiento en caché en memoria y resiliencia offline.
"""

import re
import time
import urllib.parse
from typing import Optional, Dict, Tuple
import httpx
from core.logger import logger

class ImageSearchService:
    """Servicio para buscar fotografías e ilustraciones reales para elementos de listas."""
    
    _cache: Dict[str, Tuple[float, Optional[str]]] = {}
    CACHE_TTL: float = 86400.0  # 24 horas
    MAX_CACHE_SIZE: int = 1000

    USER_AGENT_WIKI = "JarvisAssistant/4.0 (admin@jarvis-assistant.local; https://github.com/jarvis)"
    USER_AGENT_BROWSER = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )

    @classmethod
    def clean_query(cls, query: str) -> str:
        """Limpia el término de búsqueda quitando numeración, viñetas y marcas."""
        if not query:
            return ""
        s = query.strip()
        # Quitar prefijos de encabezado ###
        s = re.sub(r'^#{1,4}\s*', '', s)
        # Quitar numeración inicial y separadores (ej. "01.", "1 - ", "02: ")
        s = re.sub(r'^(?:0?\d+)?\s*[-:·.]\s*', '', s)
        s = re.sub(r'^0?\d+\s*[-:·.]?\s*', '', s)
        # Quitar negritas o cursivas de Markdown
        s = re.sub(r'[*_~`#]+', '', s)
        # Quitar emojis o caracteres gráficos residuales
        s = re.sub(r'[\U00010000-\U0010ffff]', '', s)
        # Si contiene paréntesis con subtítulo, quedarse con el concepto principal
        s = re.sub(r'\s*\([^)]*\)', '', s)
        # Quitar espacios múltiples
        s = re.sub(r'\s+', ' ', s).strip()
        return s

    @classmethod
    def clear_cache(cls):
        """Limpia la caché de imágenes."""
        cls._cache.clear()

    @classmethod
    async def search_image(cls, raw_query: str) -> Optional[str]:
        """Busca una imagen real para el término especificado con estrategia multi-proveedor."""
        term = cls.clean_query(raw_query)
        if not term or len(term) < 2:
            return None

        cache_key = term.lower()
        now = time.time()
        if cache_key in cls._cache:
            ts, cached_url = cls._cache[cache_key]
            if (now - ts) < cls.CACHE_TTL:
                return cached_url

        url = await cls._execute_search(term)
        
        # Guardar en caché (incluso None para evitar peticiones repetidas fallidas)
        if len(cls._cache) >= cls.MAX_CACHE_SIZE:
            # Purgar un 20% más antiguo
            sorted_keys = sorted(cls._cache.keys(), key=lambda k: cls._cache[k][0])
            for k in sorted_keys[:200]:
                cls._cache.pop(k, None)

        cls._cache[cache_key] = (now, url)
        return url

    @classmethod
    async def _execute_search(cls, term: str) -> Optional[str]:
        """Intenta localizar la imagen usando Wikimedia Commons, Wikipedia y Bing."""
        # 1. Probar Wikimedia Commons (máxima calidad fotográfica/ilustrativa y licencia abierta)
        img = await cls._search_wikimedia_commons(term)
        if img:
            return img

        # 2. Probar resumen enciclopédico de Wikipedia (español e inglés)
        img = await cls._search_wikipedia_summary(term)
        if img:
            return img

        # 3. Probar Bing Images (para nombres propios, platos o productos comerciales específicos)
        img = await cls._search_bing_images(term)
        if img:
            return img

        return None

    @classmethod
    async def _search_wikimedia_commons(cls, term: str) -> Optional[str]:
        """Busca imágenes de alta resolución en Wikimedia Commons."""
        api_url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "generator": "search",
            "gsrnamespace": 6,  # File: namespace
            "gsrsearch": term,
            "gsrlimit": 1,
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": 640,
            "format": "json"
        }
        headers = {
            "User-Agent": cls.USER_AGENT_WIKI,
            "Accept": "application/json"
        }
        try:
            async with httpx.AsyncClient(timeout=3.5, headers=headers, follow_redirects=True) as client:
                resp = await client.get(api_url, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    pages = data.get("query", {}).get("pages", {})
                    for _, pdata in pages.items():
                        info = pdata.get("imageinfo", [{}])[0]
                        thumb = info.get("thumburl") or info.get("url")
                        if thumb and thumb.startswith("https://"):
                            return thumb
        except Exception as e:
            logger.debug(f"[ImageService] Error en Wikimedia Commons para '{term}': {e}")
        return None

    @classmethod
    async def _search_wikipedia_summary(cls, term: str) -> Optional[str]:
        """Busca en Wikipedia (es, en) para obtener la imagen principal del artículo."""
        headers = {
            "User-Agent": cls.USER_AGENT_WIKI,
            "Accept": "application/json"
        }
        langs = ["es", "en"]
        try:
            async with httpx.AsyncClient(timeout=3.0, headers=headers, follow_redirects=True) as client:
                for lang in langs:
                    search_url = f"https://{lang}.wikipedia.org/w/api.php"
                    params = {
                        "action": "query",
                        "list": "search",
                        "srsearch": term,
                        "format": "json",
                        "utf8": 1,
                        "srlimit": 1
                    }
                    resp = await client.get(search_url, params=params)
                    if resp.status_code != 200:
                        continue
                    search_data = resp.json()
                    results = search_data.get("query", {}).get("search", [])
                    if not results:
                        continue
                    page_title = results[0]["title"]

                    summary_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(page_title)}"
                    s_resp = await client.get(summary_url)
                    if s_resp.status_code == 200:
                        s_data = s_resp.json()
                        thumb = s_data.get("thumbnail", {}).get("source")
                        if thumb and thumb.startswith("https://"):
                            return thumb
        except Exception as e:
            logger.debug(f"[ImageService] Error en Wikipedia Summary para '{term}': {e}")
        return None

    @classmethod
    async def _search_bing_images(cls, term: str) -> Optional[str]:
        """Busca imágenes en Bing Image Search como respaldo para conceptos modernos."""
        search_url = "https://www.bing.com/images/search"
        params = {"q": term, "first": 1}
        headers = {
            "User-Agent": cls.USER_AGENT_BROWSER,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
        }
        try:
            async with httpx.AsyncClient(timeout=3.5, headers=headers, follow_redirects=True) as client:
                resp = await client.get(search_url, params=params)
                if resp.status_code == 200:
                    html_content = resp.text
                    murls = re.findall(r'murl&quot;:&quot;(https://[^&"]+)&quot;', html_content)
                    for u in murls:
                        # Filtrar extensiones o dominios rotos
                        clean_u = u.replace('\\/', '/')
                        if clean_u.startswith("https://") and any(ext in clean_u.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                            return clean_u
                    # Fallback a turl (thumbnail)
                    turls = re.findall(r'turl&quot;:&quot;(https://[^&"]+)&quot;', html_content)
                    if turls:
                        return turls[0].replace('\\/', '/')
        except Exception as e:
            logger.debug(f"[ImageService] Error en Bing Images para '{term}': {e}")
        return None
