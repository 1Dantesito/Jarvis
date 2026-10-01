from typing import Dict, Any

class MusicPreferences:
    """
    Preferencias musicales dinámicas del usuario aprendidas por comportamiento.
    """
    def __init__(self):
        # Preferencias iniciales de Dante
        self.genres: Dict[str, float] = {
            "rock": 0.95,
            "alternative rock": 0.92,
            "metal": 0.85,
            "post-grunge": 0.80
        }
        self.artists: Dict[str, float] = {
            "Linkin Park": 0.98,
            "Queen": 0.90,
            "My Chemical Romance": 0.92,
            "Three Days Grace": 0.88
        }

    def adjust_artist(self, artist_name: str, delta: float):
        current = self.artists.get(artist_name, 0.5)
        new_val = max(0.1, min(1.0, current + delta))
        self.artists[artist_name] = round(new_val, 3)

    def adjust_genre(self, genre_name: str, delta: float):
        current = self.genres.get(genre_name, 0.5)
        new_val = max(0.1, min(1.0, current + delta))
        self.genres[genre_name] = round(new_val, 3)

    def get_artist_affinity(self, artist_name: str) -> float:
        for k, v in self.artists.items():
            if k.lower() in artist_name.lower() or artist_name.lower() in k.lower():
                return v
        return 0.5

    def get_top_artists(self, limit: int = 5) -> Dict[str, float]:
        sorted_a = sorted(self.artists.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_a[:limit])
