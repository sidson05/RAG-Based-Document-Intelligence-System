from typing import List, Dict
from collections import defaultdict
from ..core.models import RetrievalResult, DocumentChunk
from ..core.config import settings
from ..indexer.hybrid_store import hybrid_store
from .reranker import reranker

class HybridRetriever:
    """
    Hybrid Dense-Sparse Retriever with Reciprocal Rank Fusion (RRF)
    (Ke et al. Sec 4: Advanced Retrieval Strategies).
    """
    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k
        self.store = hybrid_store
        
    def retrieve(
        self,
        query: str,
        top_k: int = 6,
        rerank_top_n: int = 3,
        doc_id_filter: str = None
    ) -> List[RetrievalResult]:
        """
        Executes hybrid search:
        1. Dense Vector Search via FAISS
        2. Sparse Lexical Search via BM25
        3. Reciprocal Rank Fusion (RRF)
        4. Cross-Encoder Re-ranking
        """
        # Fetch dense and sparse candidates (oversample for fusion)
        sample_k = max(top_k * 2, 10)
        dense_hits = self.store.search_dense(query, top_k=sample_k)
        sparse_hits = self.store.search_sparse(query, top_k=sample_k)
        
        # If filtering by document
        if doc_id_filter:
            dense_hits = [(c, s) for c, s in dense_hits if c.doc_id == doc_id_filter]
            sparse_hits = [(c, s) for c, s in sparse_hits if c.doc_id == doc_id_filter]
            
        # Reciprocal Rank Fusion
        rrf_scores: Dict[str, float] = defaultdict(float)
        dense_score_map: Dict[str, float] = {}
        sparse_score_map: Dict[str, float] = {}
        chunk_map: Dict[str, DocumentChunk] = {}
        
        for rank, (chunk, score) in enumerate(dense_hits):
            cid = chunk.chunk_id
            chunk_map[cid] = chunk
            dense_score_map[cid] = score
            rrf_scores[cid] += 1.0 / (self.rrf_k + (rank + 1))
            
        for rank, (chunk, score) in enumerate(sparse_hits):
            cid = chunk.chunk_id
            chunk_map[cid] = chunk
            sparse_score_map[cid] = score
            rrf_scores[cid] += 1.0 / (self.rrf_k + (rank + 1))
            
        # Collect merged candidates
        candidates: List[RetrievalResult] = []
        for cid, rrf_val in rrf_scores.items():
            candidates.append(RetrievalResult(
                chunk=chunk_map[cid],
                dense_score=dense_score_map.get(cid, 0.0),
                sparse_score=sparse_score_map.get(cid, 0.0),
                rrf_score=rrf_val,
                rerank_score=0.0
            ))
            
        # Sort by RRF score first
        candidates.sort(key=lambda x: x.rrf_score, reverse=True)
        top_candidates = candidates[:top_k]
        
        # Apply Cross-Encoder Reranking
        reranked_results = reranker.rerank(query, top_candidates, top_n=rerank_top_n)
        return reranked_results

hybrid_retriever = HybridRetriever(rrf_k=settings.RRF_K)
