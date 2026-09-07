import pymupdf as fitz
from typing import List, Tuple, Optional
import uuid
from ..core.models import LayoutBlock, BlockType, BoundingBox, TableData
from .table_extractor import TableExtractor

class LayoutParser:
    """
    Document Layout Analysis (DLA) & Reading Order Reconstruction
    (aligned with Ke et al. Sec 3: Pipeline-based Document Parsing).
    
    Extracts structural blocks (Title, Header, Paragraph, Table, Footer),
    resolves multi-column reading order, and pairs each block with its exact
    spatial coordinates (bounding boxes).
    """
    
    def __init__(self):
        self.table_extractor = TableExtractor()
        
    def parse_pdf(self, pdf_path: str) -> Tuple[List[LayoutBlock], List[TableData]]:
        doc = fitz.open(pdf_path)
        blocks_all: List[LayoutBlock] = []
        
        # 1. Extract tables first so we can associate spatial regions
        extracted_tables = self.table_extractor.extract_tables_from_pdf(pdf_path)
        
        for page_idx in range(len(doc)):
            page_num = page_idx + 1
            page = doc[page_idx]
            page_rect = page.rect
            page_width = float(page_rect.width)
            page_height = float(page_rect.height)
            
            # Find tables on this page
            page_tables = [t for t in extracted_tables if t.page == page_num]
            
            # Extract raw text blocks with span information
            page_dict = page.get_text("dict")
            raw_blocks = page_dict.get("blocks", [])
            
            page_blocks: List[LayoutBlock] = []
            
            # Collect median font size to classify headers vs body
            font_sizes = []
            for b in raw_blocks:
                if b.get("type") == 0:  # text block
                    for line in b.get("lines", []):
                        for span in line.get("spans", []):
                            if span.get("text", "").strip():
                                font_sizes.append(span.get("size", 10.0))
            
            median_font_size = 10.0
            if font_sizes:
                font_sizes.sort()
                median_font_size = font_sizes[len(font_sizes) // 2]
                
            for b in raw_blocks:
                if b.get("type") != 0:
                    continue  # skip image blocks directly (handled in visual renderer)
                    
                bbox_tuple = b.get("bbox", (0, 0, 0, 0))
                b_x0, b_y0, b_x1, b_y1 = bbox_tuple
                
                # Check if this text block falls inside any detected table
                inside_table = False
                for tbl in page_tables:
                    t_bbox = tbl.bbox
                    # Overlap check
                    if (b_x0 >= t_bbox.x0 - 5 and b_x1 <= t_bbox.x1 + 5 and
                        b_y0 >= t_bbox.y0 - 5 and b_y1 <= t_bbox.y1 + 5):
                        inside_table = True
                        break
                        
                if inside_table:
                    # Skip duplicate raw text lines inside tables (table block is added separately)
                    continue
                    
                # Assemble text and determine dominant font attributes
                text_lines = []
                max_size = 0.0
                is_bold = False
                
                for line in b.get("lines", []):
                    line_text = "".join([span.get("text", "") for span in line.get("spans", [])]).strip()
                    if line_text:
                        text_lines.append(line_text)
                    for span in line.get("spans", []):
                        sz = span.get("size", 10.0)
                        if sz > max_size:
                            max_size = sz
                        flags = span.get("flags", 0)
                        if flags & 2 or "bold" in span.get("font", "").lower():
                            is_bold = True
                            
                block_text = " ".join(text_lines).strip()
                if not block_text:
                    continue
                    
                # Classify block type
                block_type = BlockType.PARAGRAPH
                if b_y1 > page_height - 40:
                    block_type = BlockType.FOOTER
                elif max_size > median_font_size * 1.5:
                    block_type = BlockType.TITLE
                elif max_size > median_font_size * 1.15 or (is_bold and len(block_text) < 120):
                    block_type = BlockType.HEADER
                elif len(block_text) < 80 and block_text.lower().startswith(("figure", "fig.", "table")):
                    block_type = BlockType.CAPTION
                    
                bbox_obj = BoundingBox(
                    x0=float(b_x0),
                    y0=float(b_y0),
                    x1=float(b_x1),
                    y1=float(b_y1),
                    page=page_num,
                    width=page_width,
                    height=page_height
                )
                
                page_blocks.append(LayoutBlock(
                    id=f"block_p{page_num}_{uuid.uuid4().hex[:6]}",
                    type=block_type,
                    text=block_text,
                    bbox=bbox_obj,
                    page=page_num,
                    reading_order=0,
                    font_size=max_size,
                    is_bold=is_bold
                ))
                
            # Add table blocks
            for tbl in page_tables:
                page_blocks.append(LayoutBlock(
                    id=f"block_table_{tbl.id}",
                    type=BlockType.TABLE,
                    text=f"[TABLE: Page {tbl.page}, {tbl.num_rows} rows x {tbl.num_cols} cols]\n{tbl.markdown}",
                    bbox=tbl.bbox,
                    page=page_num,
                    reading_order=0,
                    font_size=median_font_size,
                    is_bold=False
                ))
                
            # Sort blocks to determine reading order (reading order reconstruction)
            # Detect multi-column by checking if bounding box x-distribution divides page into columns
            sorted_blocks = self._order_blocks(page_blocks, page_width)
            for idx, blk in enumerate(sorted_blocks):
                blk.reading_order = idx + 1
                
            blocks_all.extend(sorted_blocks)
            
        doc.close()
        return blocks_all, extracted_tables

    def _order_blocks(self, blocks: List[LayoutBlock], page_width: float) -> List[LayoutBlock]:
        """
        Sorts blocks considering two-column and single-column layouts.
        """
        if not blocks:
            return []
            
        # Check if page is predominantly two-column
        midpoint = page_width / 2.0
        left_col = []
        right_col = []
        full_width = []
        
        for b in blocks:
            # Full width headers or tables spanning across columns
            if b.bbox.x0 < midpoint - 50 and b.bbox.x1 > midpoint + 50:
                full_width.append(b)
            elif b.bbox.x1 <= midpoint + 30:
                left_col.append(b)
            else:
                right_col.append(b)
                
        # If there are substantial blocks in both left and right columns without full-width overlap
        if len(left_col) >= 2 and len(right_col) >= 2:
            left_col.sort(key=lambda b: (b.bbox.y0, b.bbox.x0))
            right_col.sort(key=lambda b: (b.bbox.y0, b.bbox.x0))
            full_width.sort(key=lambda b: (b.bbox.y0, b.bbox.x0))
            
            # Merge maintaining vertical hierarchy
            result = []
            # Place full width header at top if it sits above columns
            for fw in list(full_width):
                if fw.bbox.y0 < (left_col[0].bbox.y0 if left_col else 9999):
                    result.append(fw)
                    full_width.remove(fw)
                    
            result.extend(left_col)
            result.extend(right_col)
            result.extend(full_width)
            return result
        else:
            # Standard single column or mixed layout
            blocks.sort(key=lambda b: (b.bbox.y0, b.bbox.x0))
            return blocks
