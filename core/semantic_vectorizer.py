"""
SemanticVectorizer — Vectorizador local-first de 128 dimensiones (Roadmap Fase D.3).
Utiliza el Hashing Trick (Feature Hashing) sobre n-gramas de palabras y caracteres con normalización L2,
garantizando:
  - 100% Offline / Local: Cero llamadas de red y cero consumo de cuota de API.
  - Determinismo absoluto: Mismo vector en cualquier entorno, hilo o reinicio.
  - Robustez morfológica: Tolera erratas y variaciones léxicas leves mediante sub-words.
  - Similitud coseno inmediata: Producto punto O(128) de latencia sub-milisegundo.
"""

import math
import hashlib
import unicodedata
import re
from typing import List, Union

VECTOR_DIMENSIONS = 128

def normalize_text(text: str) -> str:
    """Normaliza texto: Unicode NFD, remoción de acentos, minúsculas y limpieza de signos."""
    if not text:
        return ""
    nfd = unicodedata.normalize("NFD", text)
    stripped = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    lowered = stripped.lower()
    cleaned = re.sub(r'[^a-z0-9\s]', ' ', lowered)
    return " ".join(cleaned.split())

class LocalSemanticVectorizer:
    """
    Vectorizador denso de 128 dimensiones con hash determinista y normalización euclidiana (L2).
    """
    DIMENSIONS: int = VECTOR_DIMENSIONS

    @classmethod
    def vectorize(cls, text: str) -> List[float]:
        """
        Convierte una cadena de texto en un vector denso de 128 floats normalizado L2.
        """
        clean = normalize_text(text)
        if not clean:
            return [0.0] * cls.DIMENSIONS

        words = clean.split()
        features = []

        STOP_WORDS = {"de", "la", "el", "los", "las", "un", "una", "unos", "unas", "para", "por", "con", "sin", "en", "sobre", "su", "mi", "tu", "es", "son"}

        # 1. Unigramas de palabras (peso 2.0 para contenido, 0.5 para stopwords)
        for w in words:
            w_weight = 0.5 if w in STOP_WORDS else 2.0
            features.append((f"w:{w}", w_weight))

        # 2. Bigramas de palabras (peso 2.5)
        for i in range(len(words) - 1):
            features.append((f"bi:{words[i]}_{words[i+1]}", 2.5))

        # 3. Trigramas de caracteres para robustez morfológica (peso 0.8)
        for w in words:
            if w not in STOP_WORDS:
                if len(w) >= 3:
                    for j in range(len(w) - 2):
                        features.append((f"c3:{w[j:j+3]}", 0.8))
                else:
                    features.append((f"c3:{w}", 0.8))

        # 4. Mapeo a conceptos canónicos para puente semántico local (peso 4.0)
        CANONICAL_CONCEPTS = {
            # Gaming
            "videojuegos": "concept:gaming",
            "videojuego": "concept:gaming",
            "juegos": "concept:gaming",
            "juego": "concept:gaming",
            "gaming": "concept:gaming",
            "gamer": "concept:gaming",
            "consola": "concept:gaming",
            "consolas": "concept:gaming",
            # Cine / Películas
            "pelicula": "concept:cinema",
            "peliculas": "concept:cinema",
            "film": "concept:cinema",
            "films": "concept:cinema",
            "cine": "concept:cinema",
            # Preferencias
            "favorito": "concept:favorite",
            "favorita": "concept:favorite",
            "favoritos": "concept:favorite",
            "favoritas": "concept:favorite",
            "preferido": "concept:favorite",
            "preferida": "concept:favorite",
            "preferidos": "concept:favorite",
            "preferidas": "concept:favorite",
            "predilecto": "concept:favorite",
            "predilecta": "concept:favorite",
            "predilectos": "concept:favorite",
            "predilectas": "concept:favorite",
            # Música
            "banda": "concept:music_group",
            "grupo": "concept:music_group",
            "cancion": "concept:music",
            "canciones": "concept:music",
            "musica": "concept:music",
            "tema": "concept:music",
            "temas": "concept:music",
            "pista": "concept:music",
            # Recomendaciones
            "recomiendas": "concept:recommend",
            "recomendar": "concept:recommend",
            "recomendacion": "concept:recommend",
            "recomendaciones": "concept:recommend",
            "sugerir": "concept:recommend",
            "sugerencia": "concept:recommend",
            "sugerencias": "concept:recommend",
        }
        for w in words:
            if w in CANONICAL_CONCEPTS:
                features.append((CANONICAL_CONCEPTS[w], 4.0))
            if w.startswith("video") and len(w) > 5:
                features.append((f"w:{w[5:]}", 2.0))

        # Hashing Trick con dispersión de signo (reducción de colisiones)
        vec = [0.0] * cls.DIMENSIONS
        for feat_name, weight in features:
            h = int(hashlib.sha256(feat_name.encode("utf-8")).hexdigest()[:16], 16)
            idx = h % cls.DIMENSIONS
            sign = 1.0 if ((h >> 8) & 1) == 0 else -1.0
            vec[idx] += sign * weight

        # Normalización L2
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 1e-9:
            return [round(v / norm, 6) for v in vec]
        return [0.0] * cls.DIMENSIONS

    @classmethod
    def cosine_similarity(cls, vec_a: List[float], vec_b: List[float]) -> float:
        """
        Calcula la similitud coseno entre dos vectores normalizados L2.
        Retorna un valor entre -1.0 y 1.0 (o 0.0 si alguno es nulo).
        """
        if not vec_a or not vec_b or len(vec_a) != cls.DIMENSIONS or len(vec_b) != cls.DIMENSIONS:
            return 0.0

        # Para vectores L2 unitarios, cos(theta) = A . B
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        return max(-1.0, min(1.0, dot))
