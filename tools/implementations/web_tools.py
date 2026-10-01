import re
import html
import time
import httpx
import urllib.parse
import webbrowser
from typing import Dict, Any, Optional, Tuple
from tools.router import BaseTool, ToolType
from core.security import SecurityPolicy
from core.logger import logger

def extract_clean_text_from_html(html_content: str, max_chars: int = 4000) -> Tuple[str, str]:
    """Extrae el título y el cuerpo de texto legible de un documento HTML."""
    if not html_content:
        return "", ""

    # Extraer título
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
    title = html.unescape(title_match.group(1)).strip() if title_match else ""

    # Eliminar scripts, estilos, noscript, svg, nav, footer, header, aside, head
    text = re.sub(r'<(script|style|noscript|svg|nav|footer|header|aside|head)[^>]*>.*?</\1>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    # Eliminar comentarios HTML
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    # Reemplazar saltos de bloque por saltos de línea
    text = re.sub(r'<(p|div|h[1-6]|li|br|tr)[^>]*>', '\n', text, flags=re.IGNORECASE)
    # Eliminar todas las etiquetas restantes
    text = re.sub(r'<[^>]+>', ' ', text)
    # Decodificar entidades HTML (&amp;, &quot;, etc.)
    text = html.unescape(text)
    # Normalizar espacios
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text).strip()

    if len(text) > max_chars:
        text = text[:max_chars] + "\n... [Contenido truncado por límite de longitud]"

    return title, text

class ReadWebpageTool(BaseTool):
    name = "read_webpage"
    description = (
        "Lee, extrae e ingesta el contenido textual limpio de una página web o artículo a partir de su URL. "
        "Permite a JARVIS sintetizar documentación, noticias o artículos web para responder preguntas contextuales."
    )
    tool_type = ToolType.QUERY
    parameters_schema = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL absoluta de la página web a leer (ej. 'https://es.wikipedia.org/wiki/Inteligencia_artificial')"
            },
            "max_chars": {
                "type": "integer",
                "default": 4000,
                "description": "Cantidad máxima de caracteres a extraer (máx 10000)"
            }
        },
        "required": ["url"]
    }

    _cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
    CACHE_TTL: float = 1800.0  # 30 minutos

    @classmethod
    def clear_cache(cls):
        cls._cache.clear()

    async def execute(self, url: str, max_chars: int = 4000, **kwargs) -> Dict[str, Any]:
        is_safe, norm_url, err = SecurityPolicy.validate_url(url)
        if not is_safe or not norm_url:
            return {"success": False, "data": {}, "error": f"URL inválida o insegura: {url}"}

        now = time.time()
        # Comprobar caché semántico local
        if norm_url in self._cache:
            ts, cached_data = self._cache[norm_url]
            if (now - ts) < self.CACHE_TTL:
                data_copy = dict(cached_data)
                data_copy["cached"] = True
                return {"success": True, "data": data_copy, "error": None}

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
        }

        try:
            async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
                resp = await client.get(norm_url, headers=headers)
                if resp.status_code >= 400:
                    return {
                        "success": False,
                        "data": {"status_code": resp.status_code, "url": norm_url},
                        "error": f"El servidor web respondió con código de error HTTP {resp.status_code}."
                    }
                html_text = resp.text
        except httpx.TimeoutException:
            return {"success": False, "data": {}, "error": f"Tiempo de espera agotado al conectar con {norm_url}."}
        except Exception as e:
            logger.error(f"[ReadWebpageTool] Error descargando {norm_url}: {e}")
            return {"success": False, "data": {}, "error": f"No se pudo descargar la página: {str(e)}"}

        effective_max = min(max(max_chars, 500), 10000)
        title, clean_content = extract_clean_text_from_html(html_text, max_chars=effective_max)

        if not clean_content:
            return {
                "success": False,
                "data": {"url": norm_url, "title": title},
                "error": "No se pudo extraer contenido textual legible de la página."
            }

        result_data = {
            "url": norm_url,
            "title": title or norm_url,
            "content": clean_content,
            "char_count": len(clean_content),
            "cached": False
        }

        # Guardar en caché
        self._cache[norm_url] = (now, result_data)

        return {
            "success": True,
            "data": result_data,
            "error": None
        }

class SearchYouTubeTool(BaseTool):
    name = "search_youtube"
    description = (
        "Abre una búsqueda en YouTube en el navegador con la consulta especificada (acción visual de escritorio). "
        "Úsala SIEMPRE que el usuario pida buscar vídeos, música, tutoriales o cualquier contenido en YouTube "
        "(ej. 'busca en youtube gatitos', 'pon en youtube rock', 'busca tutorial de python en youtube')."
    )
    tool_type = ToolType.ACTION
    parameters_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Término o frase de búsqueda en YouTube"}
        },
        "required": ["query"]
    }

    async def execute(self, query: str = None, **kwargs) -> Dict[str, Any]:
        clean_query = (query or "").strip()
        if not clean_query:
            return {"success": False, "data": {}, "error": "No se especificó consulta para buscar en YouTube."}

        # Quitar prefijos comunes como 'en youtube', 'buscar' si vienen pegados
        clean_for_yt = re.sub(r'^(busca|buscar|pon|reproduce|ver)\s+(en\s+youtube\s+)?', '', clean_query, flags=re.IGNORECASE).strip()
        clean_for_yt = re.sub(r'\s+en\s+youtube$', '', clean_for_yt, flags=re.IGNORECASE).strip()
        effective_query = clean_for_yt or clean_query

        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(effective_query)}"
        webbrowser.open(search_url)
        return {
            "success": True,
            "data": {
                "query": effective_query,
                "url": search_url,
                "message": f"Buscando '{effective_query}' en YouTube."
            },
            "error": None
        }

class WebSearchTool(BaseTool):
    name = "web_search"
    description = (
        "Abre una búsqueda en Google o YouTube en el navegador predeterminado de Windows (acción visual de escritorio). "
        "Usa esta herramienta cuando el usuario pida explícitamente abrir una búsqueda o ver resultados en el navegador. "
        "Para leer o resumir páginas web sin abrir ventanas, usa 'read_webpage'."
    )
    tool_type = ToolType.ACTION
    parameters_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Término a buscar"},
            "engine": {"type": "string", "enum": ["google", "youtube"], "default": "google", "description": "Motor de búsqueda ('google' o 'youtube')"},
            "url": {"type": "string", "description": "URL directa opcional a abrir"}
        },
        "required": []
    }

    async def execute(self, query: str = None, engine: str = "google", url: str = None, **kwargs) -> Dict[str, Any]:
        if url:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            webbrowser.open(url)
            return {"success": True, "data": {"url": url, "message": f"Abriendo {url} en el navegador."}, "error": None}
        elif query:
            clean_q = query.strip()
            # Detección inteligente de búsqueda en YouTube
            if engine == "youtube" or "youtube" in clean_q.lower():
                clean_for_yt = re.sub(r'\b(en youtube|youtube)\b', '', clean_q, flags=re.IGNORECASE).strip()
                target_q = clean_for_yt or clean_q
                search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(target_q)}"
                webbrowser.open(search_url)
                return {"success": True, "data": {"query": target_q, "engine": "youtube", "url": search_url, "message": f"Buscando '{target_q}' en YouTube."}, "error": None}
            else:
                search_url = f"https://www.google.com/search?q={urllib.parse.quote(clean_q)}"
                webbrowser.open(search_url)
                return {"success": True, "data": {"query": clean_q, "engine": "google", "url": search_url, "message": f"Buscando '{clean_q}' en Google."}, "error": None}
        return {"success": False, "data": {}, "error": "No se especificó consulta ni URL para buscar."}

