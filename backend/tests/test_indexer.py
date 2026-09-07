import pytest
from pathlib import Path
from backend.app.parser.layout_parser import LayoutParser
from backend.app.indexer.chunker import HierarchicalChunker
from backend.app.indexer.hybrid_store import HybridStore
from backend.app.core.models import DocumentMetadata

SAMPLE_PDF = "data/sample_docs/benchmark_paper.pdf"

def test_hierarchical_chunker():
    parser = LayoutParser()
    blocks, tables = parser.parse_pdf(SAMPLE_PDF)
    chunker = HierarchicalChunker(max_tokens=200)
    
    chunks = chunker.chunk_document(doc_id="test_doc_1", blocks=blocks, tables=tables)
    assert len(chunks) > 0
    
    # Verify table chunk integrity
    table_chunks = [c for c in chunks if c.is_table]
    assert len(table_chunks) >= 1
    assert "TABLE" in table_chunks[0].text
    assert table_chunks[0].bbox.page == 2
    
    # Verify section hierarchy breadcrumbs
    non_table_chunks = [c for c in chunks if not c.is_table]
    assert any(len(c.section_hierarchy) > 0 for c in non_table_chunks)

def test_hybrid_store(tmp_path):
    parser = LayoutParser()
    blocks, tables = parser.parse_pdf(SAMPLE_PDF)
    chunker = HierarchicalChunker(max_tokens=200)
    chunks = chunker.chunk_document(doc_id="test_doc_1", blocks=blocks, tables=tables)
    
    store = HybridStore(index_dir=tmp_path)
    meta = DocumentMetadata(
        doc_id="test_doc_1",
        filename="benchmark_paper.pdf",
        file_path=SAMPLE_PDF,
        file_size_bytes=1024,
        num_pages=3,
        num_blocks=len(blocks),
        num_tables=len(tables),
        num_chunks=len(chunks)
    )
    
    store.add_document(meta, chunks, tables)
    
    assert len(store.chunks) == len(chunks)
    assert len(store.documents) == 1
    
    # Test dense search
    dense_results = store.search_dense("multimodal architecture pipeline", top_k=3)
    assert len(dense_results) > 0
    
    # Test sparse BM25 search for exact financial keywords
    sparse_results = store.search_sparse("Revenue Q1-2025 Net Profit", top_k=3)
    assert len(sparse_results) > 0
    # Top sparse result for table terms should be the table chunk
    assert any(c.is_table for c, s in sparse_results)
