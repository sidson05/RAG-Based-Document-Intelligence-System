import pytest
from backend.app.parser.layout_parser import LayoutParser
from backend.app.indexer.chunker import HierarchicalChunker
from backend.app.indexer.hybrid_store import HybridStore
from backend.app.retriever.hybrid_retriever import HybridRetriever
from backend.app.core.models import DocumentMetadata

SAMPLE_PDF = "data/sample_docs/benchmark_paper.pdf"

def test_hybrid_retriever(tmp_path):
    parser = LayoutParser()
    blocks, tables = parser.parse_pdf(SAMPLE_PDF)
    chunker = HierarchicalChunker()
    chunks = chunker.chunk_document(doc_id="doc_test_retriever", blocks=blocks, tables=tables)
    
    store = HybridStore(index_dir=tmp_path)
    meta = DocumentMetadata(
        doc_id="doc_test_retriever",
        filename="benchmark_paper.pdf",
        file_path=SAMPLE_PDF,
        file_size_bytes=2048,
        num_pages=3,
        num_blocks=len(blocks),
        num_tables=len(tables),
        num_chunks=len(chunks)
    )
    store.add_document(meta, chunks, tables)
    
    retriever = HybridRetriever(rrf_k=60)
    retriever.store = store
    
    # Query 1: Concept query
    results = retriever.retrieve("multimodal vision language survey 300 papers", top_k=5, rerank_top_n=3)
    assert len(results) > 0
    assert results[0].rrf_score > 0
    top_text = results[0].chunk.text.lower()
    assert "survey" in top_text or "multimodal" in top_text or "300" in top_text
    
    # Query 2: Financial table query
    table_results = retriever.retrieve("Quarterly Financial Revenue Q1 Q2 Q3 Q4", top_k=5, rerank_top_n=2)
    assert len(table_results) > 0
    # The table chunk should be ranked in the top results
    assert any(r.chunk.is_table for r in table_results)
