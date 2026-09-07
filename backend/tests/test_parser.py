import pytest
from pathlib import Path
from backend.app.parser.layout_parser import LayoutParser
from backend.app.parser.table_extractor import TableExtractor
from backend.app.parser.vision_renderer import VisionRenderer
from backend.app.core.models import BlockType

SAMPLE_PDF = "data/sample_docs/benchmark_paper.pdf"

def test_table_extractor():
    extractor = TableExtractor()
    tables = extractor.extract_tables_from_pdf(SAMPLE_PDF)
    assert len(tables) >= 1, "Should detect at least 1 table on Page 2"
    table = tables[0]
    assert table.page == 2
    assert table.num_rows == 4
    assert table.num_cols == 5
    assert "Revenue ($M)" in table.headers or any("Revenue" in h for h in table.headers)
    assert "Q1-2025" in table.markdown

def test_layout_parser():
    parser = LayoutParser()
    blocks, tables = parser.parse_pdf(SAMPLE_PDF)
    assert len(blocks) > 0
    assert len(tables) >= 1
    
    # Check block types
    types = {b.type for b in blocks}
    assert BlockType.TITLE in types or BlockType.HEADER in types
    assert BlockType.PARAGRAPH in types
    assert BlockType.TABLE in types
    
    # Check reading order
    for b in blocks:
        assert b.reading_order >= 1
        assert b.bbox.width > 0
        assert b.bbox.height > 0

def test_vision_renderer(tmp_path):
    renderer = VisionRenderer(cache_dir=tmp_path)
    page_img = renderer.render_page(SAMPLE_PDF, page_number=1)
    assert page_img.exists()
    assert page_img.suffix == ".png"
    
    # Test highlight creation
    parser = LayoutParser()
    blocks, _ = parser.parse_pdf(SAMPLE_PDF)
    first_block = blocks[0]
    highlight_img = renderer.create_highlighted_page(SAMPLE_PDF, first_block.bbox)
    assert highlight_img.exists()
