import time
import urllib.parse
from typing import Dict, Any, Optional, List, Generator
from core.sentence_buffer import SentenceBuffer
from core.response_sanitizer import ResponseSanitizer

class VoiceMetrics:
    """
    Rastreador de latencia extremo a extremo:
    speech_end -> stt_final -> llm_first_token -> sentence_ready -> tts_start -> first_audio_played -> response_end
    """
    def __init__(self):
        self.speech_end: Optional[float] = None
        self.stt_final: Optional[float] = None
        self.llm_first_token: Optional[float] = None
        self.sentence_ready: Optional[float] = None
        self.tts_start: Optional[float] = None
        self.first_audio_played: Optional[float] = None
        self.response_end: Optional[float] = None

    def mark_speech_end(self, ts: Optional[float] = None):
        self.speech_end = ts or time.time()

    def mark_audio_end(self, ts: Optional[float] = None):
        self.mark_speech_end(ts)

    def mark_stt_final(self, ts: Optional[float] = None):
        self.stt_final = ts or time.time()

    def mark_llm_first_token(self, ts: Optional[float] = None):
        if not self.llm_first_token:
            self.llm_first_token = ts or time.time()

    def mark_sentence_ready(self, ts: Optional[float] = None):
        if not self.sentence_ready:
            self.sentence_ready = ts or time.time()

    def mark_first_sentence(self, ts: Optional[float] = None):
        self.mark_sentence_ready(ts)

    def mark_tts_start(self, ts: Optional[float] = None):
        if not self.tts_start:
            self.tts_start = ts or time.time()

    def mark_first_audio_played(self, ts: Optional[float] = None):
        if not self.first_audio_played:
            self.first_audio_played = ts or time.time()

    def mark_response_end(self, ts: Optional[float] = None):
        self.response_end = ts or time.time()

    def calculate_report(self) -> Dict[str, Any]:
        report = {}
        now = time.time()
        ref_start = self.speech_end or self.stt_final or now

        if self.stt_final and self.speech_end:
            report["STT_FINAL_LATENCY_MS"] = round((self.stt_final - self.speech_end) * 1000, 2)
            report["stt_latency_ms"] = report["STT_FINAL_LATENCY_MS"]
        
        if self.llm_first_token and self.stt_final:
            report["LLM_TTFB_MS"] = round((self.llm_first_token - self.stt_final) * 1000, 2)
            report["llm_ttfb_ms"] = report["LLM_TTFB_MS"]

        if self.sentence_ready and self.stt_final:
            report["SENTENCE_LATENCY_MS"] = round((self.sentence_ready - self.stt_final) * 1000, 2)
            report["time_to_first_sentence_ms"] = report["SENTENCE_LATENCY_MS"]

        if self.tts_start and self.sentence_ready:
            report["TTS_START_LATENCY_MS"] = round((self.tts_start - self.sentence_ready) * 1000, 2)

        if self.first_audio_played and self.speech_end:
            report["TIME_TO_FIRST_AUDIO_MS"] = round((self.first_audio_played - self.speech_end) * 1000, 2)
            report["time_to_first_audio_ms"] = report["TIME_TO_FIRST_AUDIO_MS"]
        elif self.sentence_ready and self.speech_end:
            report["TIME_TO_FIRST_SENTENCE_MS"] = round((self.sentence_ready - self.speech_end) * 1000, 2)
            report["time_to_first_audio_ms"] = report["TIME_TO_FIRST_SENTENCE_MS"]

        if self.response_end and self.speech_end:
            report["TOTAL_RESPONSE_TIME_MS"] = round((self.response_end - self.speech_end) * 1000, 2)
            report["total_roundtrip_ms"] = report["TOTAL_RESPONSE_TIME_MS"]

        return report

class SentenceTTSPipeline:
    """
    Pipeline streaming de oraciones a TTS:
    Acumula tokens emitidos por el LLM y produce oraciones listas para síntesis
    en cuanto se completan delimitadores sintácticos naturales, permitiendo
    que el primer bloque de audio se empiece a reproducir inmediatamente.
    """
    def __init__(self, min_length: int = 20, max_length: int = 120, user_name: Optional[str] = None):
        self.buffer = SentenceBuffer(min_chunk_length=min_length, max_chunk_length=max_length)
        self.user_name = user_name
        self.emitted_sentences_count: int = 0

    def feed_token(self, token: str) -> List[Dict[str, Any]]:
        """
        Procesa un token entrante. Si completa una o más oraciones naturales,
        retorna una lista de paquetes de oraciones con su texto y URL de TTS listo.
        """
        raw_chunks = self.buffer.add_token(token)
        packets = []
        for c in raw_chunks:
            clean = ResponseSanitizer.sanitize(c, user_name=self.user_name)
            if clean:
                self.emitted_sentences_count += 1
                spoken = ResponseSanitizer.sanitize_for_speech(clean)
                encoded = urllib.parse.quote(spoken)
                packets.append({
                    "text": clean,
                    "spoken_text": spoken,
                    "audio_url": f"/api/tts/stream?text={encoded}",
                    "sentence_index": self.emitted_sentences_count,
                    "is_final": False
                })
        return packets

    def finish(self) -> List[Dict[str, Any]]:
        """Vacía cualquier remanente final en el buffer."""
        remaining_chunks = self.buffer.flush()
        packets = []
        for c in remaining_chunks:
            clean = ResponseSanitizer.sanitize(c, user_name=self.user_name)
            if clean:
                self.emitted_sentences_count += 1
                spoken = ResponseSanitizer.sanitize_for_speech(clean)
                encoded = urllib.parse.quote(spoken)
                packets.append({
                    "text": clean,
                    "spoken_text": spoken,
                    "audio_url": f"/api/tts/stream?text={encoded}",
                    "sentence_index": self.emitted_sentences_count,
                    "is_final": True
                })
        return packets

