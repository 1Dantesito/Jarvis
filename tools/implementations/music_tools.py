import asyncio
from typing import Dict, Any, List
from tools.router import BaseTool, ToolType
from core.music_engine import music_engine

class PlayMusicTool(BaseTool):
    name = "play_music"
    description = "Inicia la reproducción continua de música, canciones o artistas en YouTube/Spotify."
    parameters_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Nombre de la canción, artista, género o estilo a reproducir (ej. 'Linkin Park', 'algo para estudiar', 'rock clasico')"
            },
            "provider": {
                "type": "string",
                "default": "youtube",
                "description": "Proveedor opcional (youtube, spotify)"
            }
        },
        "required": ["query"]
    }

    async def execute(self, query: str, provider: str = "youtube", **kwargs) -> Dict[str, Any]:
        res = await music_engine.play_query(query, provider=provider)
        return {
            "success": res.get("success", False),
            "data": res,
            "error": None if res.get("success") else res.get("message")
        }

class SearchMusicTool(BaseTool):
    name = "search_music"
    description = "Busca canciones y devuelve una lista de resultados de pistas sin iniciar reproducción."
    parameters_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Término de búsqueda musical"}
        },
        "required": ["query"]
    }

    async def execute(self, query: str, **kwargs) -> Dict[str, Any]:
        tracks = await music_engine.search_music(query, limit=5)
        return {
            "success": True,
            "data": {
                "tracks": [t.to_dict() for t in tracks],
                "count": len(tracks),
                "message": f"Encontré {len(tracks)} canciones para '{query}'."
            },
            "error": None
        }

class PauseMusicTool(BaseTool):
    name = "pause_music"
    description = "Pausa la reproducción de música actual."
    parameters_schema = {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs) -> Dict[str, Any]:
        res = music_engine.pause()
        return {"success": True, "data": res, "error": None}

class ResumeMusicTool(BaseTool):
    name = "resume_music"
    description = "Reanuda la reproducción de música pausada."
    parameters_schema = {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs) -> Dict[str, Any]:
        res = music_engine.resume()
        return {"success": True, "data": res, "error": None}

class SkipMusicTool(BaseTool):
    name = "skip_music"
    description = "Salta a la siguiente canción en la cola de reproducción."
    parameters_schema = {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs) -> Dict[str, Any]:
        res = await music_engine.skip()
        return {"success": True, "data": res, "error": None}

class GetNowPlayingTool(BaseTool):
    name = "get_now_playing"
    description = "Consulta qué canción y artista se está reproduciendo actualmente."
    parameters_schema = {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs) -> Dict[str, Any]:
        res = music_engine.get_now_playing()
        return {"success": True, "data": res, "error": None}

class GetQueueTool(BaseTool):
    name = "get_music_queue"
    description = "Consulta las canciones próximas en la cola de reproducción."
    parameters_schema = {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs) -> Dict[str, Any]:
        res = music_engine.get_queue_summary()
        return {"success": True, "data": res, "error": None}

class ClearQueueTool(BaseTool):
    name = "clear_music_queue"
    description = "Vacía la cola de reproducción de música."
    parameters_schema = {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs) -> Dict[str, Any]:
        res = music_engine.clear_queue()
        return {"success": True, "data": res, "error": None}

class RecommendMusicTool(BaseTool):
    name = "recommend_music"
    description = "Recomienda y prepara una cola de canciones basada en preferencias, artistas afines o contexto ('algo para entrenar', 'parecido a Linkin Park')."
    tool_type = ToolType.ACTION
    parameters_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Contexto, estado de ánimo o artista de referencia"}
        },
        "required": ["query"]
    }

    async def execute(self, query: str, **kwargs) -> Dict[str, Any]:
        res = await music_engine.play_recommendations(query)
        return {"success": res.get("success", False), "data": res, "error": None}

class SearchVideosTool(BaseTool):
    name = "search_videos"
    description = "Busca vídeos de YouTube (tutoriales, documentales, entretenimiento, etc.)."
    parameters_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Término de búsqueda del vídeo"}
        },
        "required": ["query"]
    }

    async def execute(self, query: str, **kwargs) -> Dict[str, Any]:
        yt = music_engine.youtube_provider
        videos = await yt.search_videos(query, limit=5)
        return {
            "success": True,
            "data": {
                "videos": videos,
                "count": len(videos),
                "summary": f"Encontré {len(videos)} vídeos sobre '{query}'."
            },
            "error": None
        }
