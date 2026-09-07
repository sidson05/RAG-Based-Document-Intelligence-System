from typing import List, Tuple
from ..core.models import DocumentChunk, RetrievalResult
from ..core.config import settings

class CrossEncoderReranker:
    """
    Reranking Module (Ke et al. Sec 4: Context Degradation & Lost in the Middle).
    
    Scores (query, chunk_text) pairs jointly.
    Uses SentenceTransformers CrossEncoder if available, or an LLM-based scoring fallback.
    """
    def __init__(self):
        self._model = None
        self._loaded = False
        
    def _load_model(self):
        if not self._loaded:
            try:
                from sentence_transformers import CrossEncoder
                # Fast, lightweight cross-encoder
                self._model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
                self._loaded = True
            except Exception as e:
                print(f"[Reranker] Could not load cross-encoder ({e}). Will use hybrid RRF scores.")
                self._loaded = True
                self._model = None

    def rerank(self, query: str, candidates: List[RetrievalResult], top_n: int = 3) -> List[RetrievalResult]:
        if not candidates:
            return []
            
        self._load_model()
        
        if self._model is not None:
            try:
                pairs = [[query, c.chunk.text] for c in candidates]
                scores = self._model.predict(pairs)
                for c, s in zip(candidates, scores):
                    c.rerank_score = float(s)
                candidates.sort(key=lambda x: x.rerank_score, reverse=True)
                return candidates[:top_n]
            except Exception as e:
                print(f"[Reranker] CrossEncoder prediction error: {e}")
                
        # Fallback to RRF score
        candidates.sort(key=lambda x: x.rrf_score, reverse=True)
        return candidates[:top_n]

reranker = CrossEncoderReranker()
