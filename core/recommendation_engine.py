from typing import List, Dict, Any, Optional
from core.media_provider import TrackItem
from core.music_preferences import MusicPreferences
from core.music_history import MusicHistory

class RecommendationEngine:
    """
    Motor de recomendación musical explicable basado en señales, afinidad e historial.
    """
    
    CONTEXT_PRESETS = {
        "estudiar": ["rock instrumental", "rock acustico", "post-rock tranquilo", "ambient rock"],
        "tranquilo": ["rock acustico", "indie suave", "baladas rock", "musica relajante"],
        "entrenar": ["metal energico", "hard rock", "nu metal", "rock pesado"],
        "pesado": ["metalcore", "heavy metal", "thrash metal", "nu metal potente"],
        "triste": ["rock alternativo melancolico", "baladas acusticas"],
        "descubrir": ["bandas similares a Linkin Park", "rock alternativo emergente", "nu metal moderno"]
    }

    def __init__(self, preferences: MusicPreferences, history: MusicHistory):
        self.preferences = preferences
        self.history = history

    def parse_context_query(self, user_intent: str) -> str:
        low = user_intent.lower()
        for key, queries in self.CONTEXT_PRESETS.items():
            if key in low:
                return queries[0]
        return user_intent

    def score_track(self, track: TrackItem, reference_artist: Optional[str] = None) -> float:
        score = 0.5

        # 1. Afinidad con artista de referencia
        if reference_artist and reference_artist.lower() in track.artist.lower():
            score += 0.35

        # 2. Afinidad con preferencias globales del usuario
        artist_affinity = self.preferences.get_artist_affinity(track.artist)
        score += (artist_affinity - 0.5) * 0.4

        # 3. Penalización por repetición reciente
        recent_ids = self.history.get_recent_played_ids(limit=10)
        if track.id in recent_ids:
            score -= 0.5

        return round(score, 3)

    def rank_tracks(self, tracks: List[TrackItem], reference_artist: Optional[str] = None) -> List[TrackItem]:
        scored = [(t, self.score_track(t, reference_artist)) for t in tracks]
        # Ordenar de mayor a menor puntuación
        scored.sort(key=lambda x: x[1], reverse=True)
        return [t for t, _ in scored]

    def explain_recommendation(self, track: TrackItem, reference_artist: Optional[str] = None) -> str:
        affinity = self.preferences.get_artist_affinity(track.artist)
        if reference_artist and reference_artist.lower() in track.artist.lower():
            return f"Es un tema destacado de {track.artist}."
        elif affinity > 0.7:
            return f"Te gusta mucho el estilo de {track.artist} y géneros de rock alternativo."
        return f"Coincide con tus preferencias musicales de rock y metal."
