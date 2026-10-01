import time
from typing import List, Dict, Any, Optional
from core.media_provider import TrackItem

class MusicHistory:
    """
    Registro histórico de reproducciones, canciones completadas, saltadas y repetidas.
    """
    def __init__(self):
        self._history: List[Dict[str, Any]] = []

    def record_play(self, track: TrackItem):
        self._history.append({
            "track_id": track.id,
            "title": track.title,
            "artist": track.artist,
            "provider": track.provider,
            "timestamp": time.time(),
            "completed": False,
            "skipped": False,
            "replayed": False
        })
        if len(self._history) > 200:
            self._history.pop(0)

    def mark_completed(self, track_id: str):
        for item in reversed(self._history):
            if item["track_id"] == track_id:
                item["completed"] = True
                break

    def mark_skipped(self, track_id: str):
        for item in reversed(self._history):
            if item["track_id"] == track_id:
                item["skipped"] = True
                break

    def mark_replayed(self, track_id: str):
        for item in reversed(self._history):
            if item["track_id"] == track_id:
                item["replayed"] = True
                break

    def get_recent_played_ids(self, limit: int = 15) -> List[str]:
        return [item["track_id"] for item in self._history[-limit:]]

    def get_recent_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self._history[-limit:]
