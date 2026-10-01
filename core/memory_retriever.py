import math
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from core.semantic_vectorizer import LocalSemanticVectorizer

class MemoryRetriever:
    """
    Recuperador contextual de memoria con presupuesto de tokens y scoring híbrido multivariable:
    Score = Relevance(0.35) + Importance(0.25) + Confidence(0.20) + Recency(0.20)
    Relevance combina matching léxico (overlap de palabras) y similitud coseno vectorial (LocalSemanticVectorizer).
    Recency calcula decaimiento temporal exponencial real con medio-vida de 30 días.
    """

    @classmethod
    def retrieve_relevant(cls, all_memories: List[Dict[str, Any]], query: str, limit: int = 6) -> List[Dict[str, Any]]:
        if not all_memories:
            return []

        clean_q = query.lower().strip()
        words = set(re.findall(r'\w+', clean_q))
        query_vector = LocalSemanticVectorizer.vectorize(clean_q)
        
        scored = []
        for mem in all_memories:
            if not mem.get("active", True):
                continue

            mem_text = f"{mem.get('key', '')} {mem.get('value', '')} {mem.get('tags', '')}".lower()
            mem_words = set(re.findall(r'\w+', mem_text))
            
            # 1. Relevancia léxica clásica
            overlap = len(words.intersection(mem_words))
            lexical_relevance = min(1.0, overlap * 0.4)

            # 2. Relevancia semántica vectorial (128D)
            mem_vector = mem.get("vector")
            if not mem_vector:
                mem_vector = LocalSemanticVectorizer.vectorize(mem_text)
            cosine_sim = LocalSemanticVectorizer.cosine_similarity(query_vector, mem_vector)
            semantic_relevance = max(0.0, cosine_sim)

            # Relevancia híbrida
            relevance = max(lexical_relevance, semantic_relevance)
            
            if any(w in clean_q for w in ["música", "musica", "cancion", "rock", "metal"]) and mem.get("type") == "MEDIA_PREFERENCE":
                relevance = max(relevance, 0.8)
            elif any(w in clean_q for w in ["proyecto", "tesis", "jarvis", "trabajo"]) and mem.get("type") == "PROJECT":
                relevance = max(relevance, 0.85)

            importance = float(mem.get("importance", 0.5))
            confidence = float(mem.get("confidence", 0.9))

            # 3. Recency dinámica basada en decaimiento exponencial (Roadmap Fase D)
            recency = 0.20
            ts = mem.get("last_used_at") or mem.get("updated_at") or mem.get("created_at")
            if ts:
                try:
                    if isinstance(ts, str):
                        ts_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    elif isinstance(ts, datetime):
                        ts_dt = ts
                    else:
                        ts_dt = None
                    if ts_dt:
                        if ts_dt.tzinfo is None:
                            ts_dt = ts_dt.replace(tzinfo=timezone.utc)
                        delta_days = max(0.0, (datetime.now(timezone.utc) - ts_dt).total_seconds() / 86400.0)
                        recency = 0.05 + 0.15 * math.exp(-delta_days / 30.0)
                except Exception:
                    recency = 0.20

            final_score = (relevance * 0.35) + (importance * 0.25) + (confidence * 0.20) + recency
            
            if relevance > 0.1 or importance >= 0.8:
                scored.append((mem, final_score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [m for m, _ in scored[:limit]]
