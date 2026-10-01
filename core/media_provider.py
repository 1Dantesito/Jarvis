from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

class MediaCapability(str, Enum):
    DISCOVERY = "discovery"
    SEARCH = "search"
    METADATA = "metadata"
    QUEUE = "queue"
    PLAYBACK = "playback"
    RECOMMENDATIONS = "recommendations"
    HISTORY = "history"
    PREFERENCES = "preferences"

@dataclass
class TrackItem:
    id: str
    title: str
    artist: str
    provider: str = "youtube"  # youtube, spotify, local
    album: Optional[str] = None
    duration_seconds: Optional[int] = None
    uri: Optional[str] = None
    thumbnail_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "provider": self.provider,
            "album": self.album,
            "duration_seconds": self.duration_seconds,
            "uri": self.uri,
            "thumbnail_url": self.thumbnail_url,
            "metadata": self.metadata
        }

class MediaProvider(ABC):
    """
    Abstracción base para proveedores de medios y contenido.
    """
    name: str = "base_media"

    @abstractmethod
    def get_capabilities(self) -> List[MediaCapability]:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

class MusicProvider(MediaProvider):
    """
    Abstracción específica para proveedores de música (Spotify, YouTube Music, etc.).
    """
    @abstractmethod
    async def search_tracks(self, query: str, limit: int = 5) -> List[TrackItem]:
        pass

    @abstractmethod
    async def get_track_metadata(self, track_id: str) -> Optional[TrackItem]:
        pass

    @abstractmethod
    async def get_artist_top_tracks(self, artist_name: str, limit: int = 5) -> List[TrackItem]:
        pass
