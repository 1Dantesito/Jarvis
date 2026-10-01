import time
import asyncio
from typing import List, Dict, Any, Optional
from core.media_provider import MusicProvider, MediaCapability, TrackItem
from core.logger import logger

class YouTubeProvider(MusicProvider):
    name = "youtube"

    def __init__(self):
        self.ytmusic = None
        self._init_client()

    def _init_client(self):
        try:
            from ytmusicapi import YTMusic
            self.ytmusic = YTMusic()
            logger.info("[YouTubeProvider] Cliente YTMusic inicializado con éxito.")
        except Exception as e:
            logger.warning(f"[YouTubeProvider] Error inicializando YTMusic: {e}")
            self.ytmusic = None

    def get_capabilities(self) -> List[MediaCapability]:
        return [
            MediaCapability.SEARCH,
            MediaCapability.METADATA,
            MediaCapability.DISCOVERY,
            MediaCapability.PLAYBACK,
            MediaCapability.QUEUE,
            MediaCapability.RECOMMENDATIONS
        ]

    def is_available(self) -> bool:
        return self.ytmusic is not None

    async def health_check(self) -> Dict[str, Any]:
        if not self.is_available():
            return {
                "status": "error",
                "provider": self.name,
                "error": "YTMusic no inicializado."
            }

        start_t = time.time()
        try:
            tracks = await self.search_tracks("Linkin Park", limit=1)
            latency = round((time.time() - start_t) * 1000, 2)
            if tracks:
                return {
                    "status": "ok",
                    "provider": self.name,
                    "latency_ms": latency,
                    "error": None
                }
            else:
                return {
                    "status": "error",
                    "provider": self.name,
                    "latency_ms": latency,
                    "error": "Búsqueda devolvió lista vacía."
                }
        except Exception as e:
            latency = round((time.time() - start_t) * 1000, 2)
            return {
                "status": "error",
                "provider": self.name,
                "latency_ms": latency,
                "error": str(e)
            }

    async def search_tracks(self, query: str, limit: int = 5) -> List[TrackItem]:
        if not self.ytmusic:
            return []

        def _sync_search():
            try:
                results = self.ytmusic.search(query, filter="songs", limit=limit)
                items = []
                for r in results:
                    v_id = r.get("videoId")
                    if not v_id:
                        continue
                    artist_str = ", ".join([a["name"] for a in r.get("artists", [])]) or "Artista"
                    album_str = r.get("album", {}).get("name") if isinstance(r.get("album"), dict) else None
                    items.append(TrackItem(
                        id=v_id,
                        title=r.get("title", "Canción"),
                        artist=artist_str,
                        provider=self.name,
                        album=album_str,
                        duration_seconds=r.get("duration_seconds")
                    ))
                return items
            except Exception as e:
                logger.error(f"[YouTubeProvider] Error en búsqueda de canciones: {e}")
                return []

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _sync_search)

    async def search_videos(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Búsqueda de vídeos generales (tutoriales, entretenimiento, etc.).
        """
        if not self.ytmusic:
            return []

        def _sync_search():
            try:
                results = self.ytmusic.search(query, filter="videos", limit=limit)
                videos = []
                for r in results:
                    v_id = r.get("videoId")
                    if v_id:
                        videos.append({
                            "id": v_id,
                            "title": r.get("title", "Video"),
                            "channel": ", ".join([a["name"] for a in r.get("artists", [])]),
                            "url": f"https://www.youtube.com/watch?v={v_id}"
                        })
                return videos
            except Exception as e:
                logger.error(f"[YouTubeProvider] Error buscando videos: {e}")
                return []

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _sync_search)

    async def get_track_metadata(self, track_id: str) -> Optional[TrackItem]:
        tracks = await self.search_tracks(track_id, limit=1)
        return tracks[0] if tracks else None

    async def get_artist_top_tracks(self, artist_name: str, limit: int = 5) -> List[TrackItem]:
        return await self.search_tracks(artist_name, limit=limit)
