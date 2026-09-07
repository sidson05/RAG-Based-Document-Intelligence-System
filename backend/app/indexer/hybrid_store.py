import json
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import faiss
import numpy as np
from rank_bm25 import BM25Okapi

from ..core.models import DocumentChunk, DocumentMetadata, TableData
from ..core.config import settings
from .embeddings import embedding_service

class HybridStore:
    """
    Hybrid Index Store combining:
    1. Dense Vector Index (FAISS IndexFlatIP)
    2. Sparse Lexical Index (BM25Okapi)
    3. Document and Table Metadata Repositories
    """
    
    def __init__(self, index_dir: Optional[Path] = None):
        self.index_dir = index_dir or settings.INDEX_DIR
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        self.chunks: List[DocumentChunk] = []
        self.chunk_id_map: Dict[str, DocumentChunk] = {}
        self.documents: Dict[str, DocumentMetadata] = {}
        self.tables: Dict[str, TableData] = {}
        
        self.faiss_index: Optional[faiss.IndexFlatIP] = None
        self.bm25_index: Optional[BM25Okapi] = None
        self.tokenized_corpus: List[List[str]] = []
        
        self.embedding_dim: Optional[int] = None
        self._load_if_exists()

    def _tokenize(self, text: str) -> List[str]:
        return text.lower().replace("\n", " ").replace(".", " ").replace(",", " ").split()

    def add_document(
        self,
        doc_meta: DocumentMetadata,
        chunks: List[DocumentChunk],
        tables: Optional[List[TableData]] = None
    ):
        """
        Indexes chunks for a new document into both FAISS and BM25.
        """
        self.documents[doc_meta.doc_id] = doc_meta
        if tables:
            for t in tables:
                self.tables[t.id] = t
                
        if not chunks:
            return
            
        texts = [c.text for c in chunks]
        vectors = embedding_service.embed_texts(texts)
        
        # Init or extend FAISS
        if self.faiss_index is None:
            self.embedding_dim = vectors.shape[1]
            self.faiss_index = faiss.IndexFlatIP(self.embedding_dim)
            
        self.faiss_index.add(vectors)
        
        start_idx = len(self.chunks)
        self.chunks.extend(chunks)
        for c in chunks:
            self.chunk_id_map[c.chunk_id] = c
            
        # Update BM25
        for c in chunks:
            self.tokenized_corpus.append(self._tokenize(c.text))
        self.bm25_index = BM25Okapi(self.tokenized_corpus)
        
        self.save()

    def search_dense(self, query: str, top_k: int = 10) -> List[Tuple[DocumentChunk, float]]:
        if self.faiss_index is None or self.faiss_index.ntotal == 0:
            return []
            
        q_vec = embedding_service.embed_query(query).reshape(1, -1)
        k = min(top_k, self.faiss_index.ntotal)
        scores, indices = self.faiss_index.search(q_vec, k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self.chunks):
                results.append((self.chunks[idx], float(score)))
        return results

    def search_sparse(self, query: str, top_k: int = 10) -> List[Tuple[DocumentChunk, float]]:
        if self.bm25_index is None or not self.chunks:
            return []
            
        tokens = self._tokenize(query)
        if not tokens:
            return []
            
        scores = self.bm25_index.get_scores(tokens)
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score > 0.0:
                results.append((self.chunks[idx], score))
        return results

    def get_table_by_id(self, table_id: str) -> Optional[TableData]:
        return self.tables.get(table_id)

    def get_chunks_for_doc(self, doc_id: str) -> List[DocumentChunk]:
        return [c for c in self.chunks if c.doc_id == doc_id]

    def save(self):
        """Persists index and metadata to disk."""
        meta_file = self.index_dir / "store_meta.pkl"
        with open(meta_file, "wb") as f:
            pickle.dump({
                "chunks": [c.model_dump() for c in self.chunks],
                "documents": {k: v.model_dump() for k, v in self.documents.items()},
                "tables": {k: v.model_dump() for k, v in self.tables.items()},
                "tokenized_corpus": self.tokenized_corpus,
                "embedding_dim": self.embedding_dim
            }, f)
            
        if self.faiss_index is not None:
            faiss_file = self.index_dir / "faiss.index"
            faiss.write_index(self.faiss_index, str(faiss_file))

    def _load_if_exists(self):
        meta_file = self.index_dir / "store_meta.pkl"
        faiss_file = self.index_dir / "faiss.index"
        
        if meta_file.exists() and faiss_file.exists():
            try:
                with open(meta_file, "rb") as f:
                    data = pickle.load(f)
                    
                self.chunks = [DocumentChunk(**c) for c in data["chunks"]]
                self.chunk_id_map = {c.chunk_id: c for c in self.chunks}
                self.documents = {k: DocumentMetadata(**v) for k, v in data["documents"].items()}
                self.tables = {k: TableData(**v) for k, v in data["tables"].items()}
                self.tokenized_corpus = data["tokenized_corpus"]
                self.embedding_dim = data.get("embedding_dim")
                
                if self.tokenized_corpus:
                    self.bm25_index = BM25Okapi(self.tokenized_corpus)
                    
                self.faiss_index = faiss.read_index(str(faiss_file))
                print(f"[HybridStore] Loaded {len(self.chunks)} chunks and {len(self.documents)} documents from disk.")
            except Exception as e:
                print(f"[HybridStore] Error loading saved indices: {e}. Starting fresh.")
                self.chunks = []
                self.chunk_id_map = {}
                self.documents = {}
                self.tables = {}
                self.faiss_index = None
                self.bm25_index = None
                self.tokenized_corpus = []

hybrid_store = HybridStore()
