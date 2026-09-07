import os
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

from typing import List
import numpy as np
from ..core.config import settings

class EmbeddingService:
    """
    Embedding Service supporting:
    1. Google GenAI Embeddings (models/gemini-embedding-001)
    2. Local SentenceTransformers (all-MiniLM-L6-v2) as reliable offline fallback
    """
    def __init__(self):
        self._genai_client = None
        self._local_model = None
        self._use_gemini = bool(settings.GEMINI_API_KEY)
        
        if self._use_gemini:
            try:
                from google import genai
                self._genai_client = genai.Client()
            except Exception as e:
                print(f"[EmbeddingService] Warning: Failed to init GenAI client: {e}. Falling back to local model.")
                self._use_gemini = False

    def _get_local_model(self):
        if self._local_model is None:
            from sentence_transformers import SentenceTransformer
            print(f"[EmbeddingService] Loading local embedding model: {settings.LOCAL_EMBEDDING_MODEL}")
            self._local_model = SentenceTransformer(settings.LOCAL_EMBEDDING_MODEL)
        return self._local_model

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Embeds a batch of texts into normalized float32 numpy vector array.
        """
        if not texts:
            return np.empty((0, 3072 if self._use_gemini else 384), dtype=np.float32)

        if self._use_gemini and self._genai_client:
            try:
                results = []
                # Batch in groups of 20
                for i in range(0, len(texts), 20):
                    batch = texts[i:i+20]
                    for t in batch:
                        res = self._genai_client.models.embed_content(
                            model=settings.EMBEDDING_MODEL,
                            contents=t
                        )
                        results.append(res.embeddings[0].values)
                arr = np.array(results, dtype=np.float32)
                norms = np.linalg.norm(arr, axis=1, keepdims=True)
                norms[norms == 0] = 1.0
                return arr / norms
            except Exception as e:
                print(f"[EmbeddingService] GenAI embedding call failed ({e}), falling back to local model.")
                self._use_gemini = False

        # Fallback to local SentenceTransformer
        model = self._get_local_model()
        vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return np.array(vectors, dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embeds a single query string into a normalized 1D vector.
        """
        if self._use_gemini and self._genai_client:
            try:
                res = self._genai_client.models.embed_content(
                    model=settings.EMBEDDING_MODEL,
                    contents=query
                )
                vec = np.array(res.embeddings[0].values, dtype=np.float32)
                norm = np.linalg.norm(vec)
                return vec / (norm if norm != 0 else 1.0)
            except Exception as e:
                print(f"[EmbeddingService] GenAI query embedding failed: {e}")
                self._use_gemini = False

        model = self._get_local_model()
        vec = model.encode(query, normalize_embeddings=True)
        return np.array(vec, dtype=np.float32)

embedding_service = EmbeddingService()
