from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class SpeechToTextProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, mime_type: str = "audio/webm") -> str:
        pass

class TextToSpeechProvider(ABC):
    @abstractmethod
    async def synthesize(self, text: str, output_path: str) -> str:
        pass

class MusicProvider(ABC):
    @abstractmethod
    async def search_songs(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        pass
