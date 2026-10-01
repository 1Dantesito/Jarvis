import re
from typing import List, Generator, Optional

class SentenceBuffer:
    """
    Buffer para fragmentar texto de streaming en frases o cláusulas naturales
    óptimas para síntesis de voz (TTS) de baja latencia sin pausas artificiales.
    """
    
    STRONG_DELIMITERS = re.compile(r'([.?!\n]+)\s*')
    CLAUSE_DELIMITERS = re.compile(r'([,:;]+)\s*')

    def __init__(self, min_chunk_length: int = 55, max_chunk_length: int = 140):
        self.min_chunk_length = min_chunk_length
        self.max_chunk_length = max_chunk_length
        self._buffer: str = ""

    def add_token(self, token: str) -> List[str]:
        self._buffer += token
        ready_chunks = []

        while True:
            chunk = self._extract_next_chunk()
            if chunk:
                cleaned = self.clean_for_speech(chunk)
                if cleaned:
                    ready_chunks.append(cleaned)
            else:
                break

        return ready_chunks

    def flush(self) -> List[str]:
        remaining = self._buffer.strip()
        self._buffer = ""
        if remaining:
            cleaned = self.clean_for_speech(remaining)
            if cleaned:
                return [cleaned]
        return []

    def _extract_next_chunk(self) -> Optional[str]:
        # 1. Delimitadores fuertes (. ? ! \n)
        match_strong = self.STRONG_DELIMITERS.search(self._buffer)
        if match_strong:
            end_pos = match_strong.end()
            chunk = self._buffer[:end_pos].strip()
            self._buffer = self._buffer[end_pos:]
            return chunk

        # 2. Cláusulas y comas si supera la longitud mínima
        if len(self._buffer) >= self.min_chunk_length:
            match_clause = self.CLAUSE_DELIMITERS.search(self._buffer)
            if match_clause and match_clause.end() >= self.min_chunk_length:
                end_pos = match_clause.end()
                chunk = self._buffer[:end_pos].strip()
                self._buffer = self._buffer[end_pos:]
                return chunk

        # 3. Si excede el máximo permitido sin signos
        if len(self._buffer) >= self.max_chunk_length:
            last_space = self._buffer.rfind(" ")
            if last_space > self.min_chunk_length:
                chunk = self._buffer[:last_space].strip()
                self._buffer = self._buffer[last_space + 1:]
                return chunk

        return None

    @classmethod
    def clean_for_speech(cls, text: str) -> str:
        if not text:
            return ""
        s = re.sub(r'[*#_~>|]', '', text)
        s = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', s)
        s = re.sub(r'\s+', ' ', s).strip()
        return s
