import random
from typing import List, Optional, Dict, Any
from core.media_provider import TrackItem

class MusicQueue:
    """
    Cola de reproducción musical con soporte de next, previous, shuffle, repeat.
    """
    def __init__(self):
        self._queue: List[TrackItem] = []
        self._current_index: int = -1
        self.repeat_mode: bool = False

    def add_track(self, track: TrackItem):
        self._queue.append(track)
        if self._current_index == -1:
            self._current_index = 0

    def add_multiple(self, tracks: List[TrackItem]):
        for t in tracks:
            self.add_track(t)

    def get_current(self) -> Optional[TrackItem]:
        if 0 <= self._current_index < len(self._queue):
            return self._queue[self._current_index]
        return None

    def next_track(self) -> Optional[TrackItem]:
        if not self._queue:
            return None
        if self._current_index + 1 < len(self._queue):
            self._current_index += 1
            return self._queue[self._current_index]
        elif self.repeat_mode and self._queue:
            self._current_index = 0
            return self._queue[0]
        return None

    def previous_track(self) -> Optional[TrackItem]:
        if not self._queue:
            return None
        if self._current_index > 0:
            self._current_index -= 1
            return self._queue[self._current_index]
        return self._queue[0]

    def clear(self):
        self._queue = []
        self._current_index = -1

    def get_upcoming(self, limit: int = 10) -> List[TrackItem]:
        if self._current_index == -1 or self._current_index >= len(self._queue):
            return []
        return self._queue[self._current_index + 1 : self._current_index + 1 + limit]

    def is_empty(self) -> bool:
        return len(self._queue) == 0 or self._current_index >= len(self._queue)

    def size(self) -> int:
        return len(self._queue)

    def remaining_count(self) -> int:
        if self._current_index == -1:
            return len(self._queue)
        return max(0, len(self._queue) - self._current_index - 1)


class SmartQueue:
    """
    Cola Inteligente que mantiene un buffer saludable de reproducción continua.
    """
    TARGET_BUFFER_SIZE = 10
    REFILL_THRESHOLD = 3

    def __init__(self, music_queue: MusicQueue):
        self.queue = music_queue

    def needs_refill(self) -> bool:
        return self.queue.remaining_count() < self.REFILL_THRESHOLD

    def add_smart_tracks(self, new_tracks: List[TrackItem]):
        existing_ids = {t.id for t in self.queue._queue}
        clean_tracks = [t for t in new_tracks if t.id not in existing_ids]
        self.queue.add_multiple(clean_tracks)
