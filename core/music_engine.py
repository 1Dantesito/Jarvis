import re
import asyncio
import unicodedata
from typing import Dict, Any, List, Optional
from core.media_provider import TrackItem
from core.spotify_provider import SpotifyProvider
from core.youtube_provider import YouTubeProvider
from core.music_history import MusicHistory
from core.music_preferences import MusicPreferences
from core.recommendation_engine import RecommendationEngine
from core.music_queue import MusicQueue, SmartQueue
from core.logger import logger

_NOISE_WORDS = re.compile(
    r'\b(cover|karaoke|tribute|tribute band|live|en vivo|acoustic|acustico|'
    r'instrumental|remix|version|versión|remastered|remasterizado)\b',
    re.IGNORECASE
)

class PlaybackState:
    IDLE = "IDLE"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"

class MusicEngine:
    """
    Motor Multimedia Central de JARVIS: coordina proveedores, cola, reproducción y recomendaciones.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MusicEngine, cls).__new__(cls)
            cls._instance._init_engine()
        return cls._instance

    def _init_engine(self):
        self.youtube_provider = YouTubeProvider()
        self.spotify_provider = SpotifyProvider()
        self.history = MusicHistory()
        self.preferences = MusicPreferences()
        self.recommendations = RecommendationEngine(self.preferences, self.history)
        self.queue = MusicQueue()
        self.smart_queue = SmartQueue(self.queue)
        self.playback_state = PlaybackState.IDLE
        self.current_reference_artist = None

    async def search_music(self, query: str, provider: str = "youtube", limit: int = 5) -> List[TrackItem]:
        clean_q = self.recommendations.parse_context_query(query)
        if provider == "spotify" and self.spotify_provider.is_available():
            tracks = await self.spotify_provider.search_tracks(clean_q, limit=limit)
            if tracks:
                return tracks

        # Default a YouTube
        return await self.youtube_provider.search_tracks(clean_q, limit=limit)

    @staticmethod
    def _normalize_title(title: str) -> str:
        t = title.lower()
        t = re.sub(r'\(.*?\)|\[.*?\]', ' ', t)      # quita "(Live)", "(Cover)", etc.
        t = _NOISE_WORDS.sub(' ', t)
        t = ''.join(c for c in unicodedata.normalize('NFKD', t) if not unicodedata.combining(c))
        t = re.sub(r'[^a-z0-9]+', ' ', t).strip()
        return t

    async def play_query(self, query: str, provider: str = "youtube") -> Dict[str, Any]:
        """
        Inicia reproducción continua y llena la cola inteligente con recomendaciones.
        """
        clean_q = self.recommendations.parse_context_query(query)
        # parse_context_query solo transforma el texto si matcheó un preset de ánimo/género;
        # si devolvió el mismo texto, es porque el usuario pidió algo puntual (canción/artista).
        is_specific_request = (clean_q == query)

        raw_tracks = await self.search_music(clean_q, provider=provider, limit=15 if is_specific_request else 8)
        if not raw_tracks:
            return {"success": False, "message": f"No encontré canciones para '{query}'.", "playlist": []}

        # Deduplicar por título normalizado, quedándonos con la primera aparición (mejor ranking de YTMusic)
        seen, deduped = set(), []
        for t in raw_tracks:
            key = self._normalize_title(t.title)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(t)

        if is_specific_request and deduped:
            primary = deduped[0]
            self.current_reference_artist = primary.artist
            seen_titles = {self._normalize_title(primary.title)}
            extra_tracks = []

            # 1. Completar con OTRAS canciones del mismo artista, no más copias del mismo título
            if primary.artist and primary.artist.lower() not in ["artista", "various artists", "desconocido"]:
                artist_tracks = await self.youtube_provider.get_artist_top_tracks(primary.artist, limit=8)
                for t in artist_tracks:
                    key = self._normalize_title(t.title)
                    if key not in seen_titles:
                        seen_titles.add(key)
                        extra_tracks.append(t)

            # 2. Si faltan canciones, completar con los otros temas únicos de la búsqueda inicial
            for t in deduped[1:]:
                key = self._normalize_title(t.title)
                if key not in seen_titles and len(extra_tracks) < 7:
                    seen_titles.add(key)
                    extra_tracks.append(t)

            tracks = [primary] + extra_tracks
        else:
            self.current_reference_artist = deduped[0].artist if deduped else None
            tracks = deduped

        # Inicializar cola
        self.queue.clear()
        ranked = self.recommendations.rank_tracks(tracks, reference_artist=self.current_reference_artist)
        self.queue.add_multiple(ranked)
        self.playback_state = PlaybackState.PLAYING

        current = self.queue.get_current()
        if current:
            self.history.record_play(current)

        # Generar lista de IDs y objetos tracks para el frontend
        playlist_ids = [t.id for t in self.queue._queue if t.provider == "youtube"]
        tracks_list = [t.to_dict() for t in self.queue._queue]
        return {
            "success": True,
            "status": "PLAYBACK_STARTED",
            "current_track": current.to_dict() if current else None,
            "playlist": playlist_ids,
            "tracks": tracks_list,
            "total_queued": self.queue.size(),
            "message": f"Reproduciendo {current.title} de {current.artist}." if current else "Iniciando lista."
        }

    async def play_recommendations(self, context_or_artist: str) -> Dict[str, Any]:
        """
        Genera y reproduce una cola de descubrimiento explicable.
        """
        tracks = await self.search_music(context_or_artist, limit=8)
        if not tracks:
            return {"success": False, "message": "No encontré recomendaciones.", "playlist": []}

        first_track = tracks[0]
        self.current_reference_artist = first_track.artist
        self.queue.clear()
        self.queue.add_multiple(tracks)
        self.playback_state = PlaybackState.PLAYING

        current = self.queue.get_current()
        if current:
            self.history.record_play(current)
            explanation = self.recommendations.explain_recommendation(current, self.current_reference_artist)
        else:
            explanation = "Selección lista."

        playlist_ids = [t.id for t in self.queue._queue if t.provider == "youtube"]
        tracks_list = [t.to_dict() for t in self.queue._queue]
        return {
            "success": True,
            "status": "PLAYBACK_STARTED",
            "current_track": current.to_dict() if current else None,
            "playlist": playlist_ids,
            "tracks": tracks_list,
            "explanation": explanation,
            "message": f"Preparé recomendaciones: {explanation}"
        }

    def pause(self) -> Dict[str, Any]:
        self.playback_state = PlaybackState.PAUSED
        return {"success": True, "status": "PAUSED", "message": "Reproducción pausada."}

    def resume(self) -> Dict[str, Any]:
        self.playback_state = PlaybackState.PLAYING
        current = self.queue.get_current()
        return {
            "success": True,
            "status": "PLAYING",
            "current_track": current.to_dict() if current else None,
            "message": f"Reanudando {current.title}." if current else "Reanudando."
        }

    async def skip(self) -> Dict[str, Any]:
        current = self.queue.get_current()
        if current:
            self.history.mark_skipped(current.id)
            self.preferences.adjust_artist(current.artist, -0.05)

        next_t = self.queue.next_track()
        if next_t:
            self.history.record_play(next_t)
            # Rellenar cola si queda poco contenido
            if self.smart_queue.needs_refill() and self.current_reference_artist:
                more_tracks = await self.youtube_provider.get_artist_top_tracks(self.current_reference_artist, limit=5)
                self.smart_queue.add_smart_tracks(more_tracks)

            return {
                "success": True,
                "status": "TRACK_SKIPPED",
                "next_track": next_t.to_dict(),
                "message": f"Siguiente: {next_t.title} de {next_t.artist}."
            }
        else:
            self.playback_state = PlaybackState.STOPPED
            return {"success": True, "status": "QUEUE_EMPTY", "message": "Fin de la cola de reproducción."}

    def on_track_completed(self, track_id: Optional[str] = None):
        current = self.queue.get_current()
        if current:
            self.history.mark_completed(current.id)
            self.preferences.adjust_artist(current.artist, 0.05)

    def get_now_playing(self) -> Dict[str, Any]:
        current = self.queue.get_current()
        if not current or self.playback_state == PlaybackState.IDLE:
            return {
                "is_playing": False,
                "playback_state": self.playback_state,
                "track": None,
                "summary": "No hay nada reproduciéndose en este momento."
            }
        return {
            "is_playing": self.playback_state == PlaybackState.PLAYING,
            "playback_state": self.playback_state,
            "track": current.to_dict(),
            "summary": f"Estás escuchando {current.title} de {current.artist} ({current.provider})."
        }

    def get_queue_summary(self) -> Dict[str, Any]:
        upcoming = self.queue.get_upcoming(limit=5)
        current = self.queue.get_current()
        return {
            "current": current.to_dict() if current else None,
            "upcoming": [t.to_dict() for t in upcoming],
            "total_remaining": self.queue.remaining_count(),
            "summary": f"En cola: {len(upcoming)} canciones próximas." if upcoming else "La cola está vacía."
        }

    def clear_queue(self) -> Dict[str, Any]:
        self.queue.clear()
        self.playback_state = PlaybackState.STOPPED
        return {"success": True, "message": "Cola de reproducción vaciada."}

music_engine = MusicEngine()
