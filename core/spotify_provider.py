import os
import asyncio
from enum import Enum
from typing import List, Dict, Any, Optional
from core.media_provider import MusicProvider, MediaCapability, TrackItem
from core.config import settings
from core.logger import logger

class SpotifyConnectionStatus(str, Enum):
    NOT_CONNECTED = "NOT_CONNECTED"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    PREMIUM_REQUIRED = "PREMIUM_REQUIRED"
    NO_ACTIVE_DEVICE = "NO_ACTIVE_DEVICE"
    AVAILABLE = "AVAILABLE"

class SpotifyProvider(MusicProvider):
    name = "spotify"

    def __init__(self):
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID", "")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET", "")
        self.client = None
        self._init_client()

    def _init_client(self):
        if self.client_id and self.client_secret and self.client_id != "your_spotify_client_id_here":
            try:
                import spotipy
                from spotipy.oauth2 import SpotifyClientCredentials
                auth_manager = SpotifyClientCredentials(client_id=self.client_id, client_secret=self.client_secret)
                self.client = spotipy.Spotify(auth_manager=auth_manager)
                logger.info("[SpotifyProvider] Cliente Spotify inicializado con éxito.")
            except Exception as e:
                logger.warning(f"[SpotifyProvider] Error inicializando Spotipy: {e}")
                self.client = None

    def get_capabilities(self) -> List[MediaCapability]:
        return [MediaCapability.SEARCH, MediaCapability.METADATA, MediaCapability.DISCOVERY]

    def is_available(self) -> bool:
        return self.client is not None

    def get_status(self) -> SpotifyConnectionStatus:
        if not self.client_id or not self.client_secret or self.client_id == "your_spotify_client_id_here":
            return SpotifyConnectionStatus.NOT_CONNECTED
        if not self.client:
            return SpotifyConnectionStatus.AUTH_REQUIRED
        return SpotifyConnectionStatus.AVAILABLE

    async def health_check(self) -> Dict[str, Any]:
        if not self.is_available():
            return {
                "status": "not_configured" if not self.client_id else "error",
                "provider": self.name,
                "error": "Credenciales de Spotify no configuradas."
            }
        try:
            loop = asyncio.get_running_loop()
            res = await loop.run_in_executor(None, lambda: self.client.search(q="rock", type="track", limit=1))
            if res and "tracks" in res:
                return {"status": "ok", "provider": self.name, "error": None}
            return {"status": "error", "provider": self.name, "error": "Sin resultados"}
        except Exception as e:
            return {"status": "error", "provider": self.name, "error": str(e)}

    async def search_tracks(self, query: str, limit: int = 5) -> List[TrackItem]:
        if not self.client:
            logger.debug("[SpotifyProvider] Cliente no conectado. Búsqueda abortada.")
            return []

        def _sync_search():
            try:
                res = self.client.search(q=query, type="track", limit=limit)
                tracks = []
                if res and "tracks" in res and "items" in res["tracks"]:
                    for item in res["tracks"]["items"]:
                        artist_name = item["artists"][0]["name"] if item["artists"] else "Desconocido"
                        album_name = item["album"]["name"] if "album" in item else None
                        tracks.append(TrackItem(
                            id=item["id"],
                            title=item["name"],
                            artist=artist_name,
                            provider=self.name,
                            album=album_name,
                            duration_seconds=int(item["duration_ms"] / 1000) if "duration_ms" in item else None,
                            uri=item.get("uri")
                        ))
                return tracks
            except Exception as e:
                logger.error(f"[SpotifyProvider] Error en búsqueda síncrona: {e}")
                return []

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _sync_search)

    async def get_track_metadata(self, track_id: str) -> Optional[TrackItem]:
        if not self.client:
            return None

        def _sync_meta():
            try:
                item = self.client.track(track_id)
                if item:
                    artist_name = item["artists"][0]["name"] if item["artists"] else "Desconocido"
                    return TrackItem(
                        id=item["id"],
                        title=item["name"],
                        artist=artist_name,
                        provider=self.name,
                        album=item.get("album", {}).get("name"),
                        duration_seconds=int(item.get("duration_ms", 0) / 1000),
                        uri=item.get("uri")
                    )
            except Exception as e:
                logger.error(f"[SpotifyProvider] Error obteniendo track: {e}")
            return None

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _sync_meta)

    async def get_artist_top_tracks(self, artist_name: str, limit: int = 5) -> List[TrackItem]:
        if not self.client:
            return []

        def _sync_artist():
            try:
                search_res = self.client.search(q=artist_name, type="artist", limit=1)
                if search_res and search_res["artists"]["items"]:
                    artist_id = search_res["artists"]["items"][0]["id"]
                    top = self.client.artist_top_tracks(artist_id)
                    tracks = []
                    for item in top.get("tracks", [])[:limit]:
                        tracks.append(TrackItem(
                            id=item["id"],
                            title=item["name"],
                            artist=artist_name,
                            provider=self.name,
                            album=item.get("album", {}).get("name"),
                            duration_seconds=int(item.get("duration_ms", 0) / 1000),
                            uri=item.get("uri")
                        ))
                    return tracks
            except Exception as e:
                logger.error(f"[SpotifyProvider] Error obteniendo top tracks: {e}")
            return []

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _sync_artist)
