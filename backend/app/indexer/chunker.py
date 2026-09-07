from typing import List, Optional
import uuid
from ..core.models import LayoutBlock, BlockType, DocumentChunk, BoundingBox, TableData
from ..core.config import settings

class HierarchicalChunker:
    """
    Structure-Aware Hierarchical Chunker (Ke et al. Sec 4: Document Chunking).
    
    Preserves document section tree hierarchy, avoids slicing tables mid-cell,
    and calculates unified spatial bounding boxes across aggregated blocks.
    """
    
    def __init__(self, max_tokens: int = 500, overlap_tokens: int = 50):
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        
    def _approx_tokens(self, text: str) -> int:
        return max(1, len(text.split()))

    def chunk_document(
        self,
        doc_id: str,
        blocks: List[LayoutBlock],
        tables: Optional[List[TableData]] = None
    ) -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []
        current_section_path: List[str] = []
        
        # Buffer for aggregating continuous text blocks
        curr_text_parts: List[str] = []
        curr_blocks: List[LayoutBlock] = []
        curr_page: int = 1
        
        def flush_current_chunk():
            nonlocal curr_text_parts, curr_blocks, curr_page
            if not curr_blocks:
                return
                
            combined_text = "\n\n".join(curr_text_parts).strip()
            if not combined_text:
                curr_text_parts = []
                curr_blocks = []
                return
                
            # Prepend breadcrumbs context
            prefix = ""
            if current_section_path:
                prefix = f"[{' > '.join(current_section_path)}]\n"
            full_chunk_text = prefix + combined_text
            
            # Compute union bounding box for all blocks in this chunk on this page
            p_blocks = [b for b in curr_blocks if b.page == curr_page]
            if p_blocks:
                min_x = min(b.bbox.x0 for b in p_blocks)
                min_y = min(b.bbox.y0 for b in p_blocks)
                max_x = max(b.bbox.x1 for b in p_blocks)
                max_y = max(b.bbox.y1 for b in p_blocks)
                w = p_blocks[0].bbox.width
                h = p_blocks[0].bbox.height
            else:
                min_x, min_y, max_x, max_y, w, h = 0, 0, 0, 0, 0, 0
                
            union_bbox = BoundingBox(
                x0=min_x, y0=min_y, x1=max_x, y1=max_y,
                page=curr_page, width=w, height=h
            )
            
            chunk_id = f"chunk_{doc_id}_{len(chunks)+1}_{uuid.uuid4().hex[:4]}"
            
            chunks.append(DocumentChunk(
                chunk_id=chunk_id,
                doc_id=doc_id,
                text=full_chunk_text,
                page=curr_page,
                bbox=union_bbox,
                section_hierarchy=list(current_section_path),
                is_table=False,
                metadata={
                    "num_blocks": len(curr_blocks),
                    "approx_tokens": self._approx_tokens(full_chunk_text)
                }
            ))
            
            curr_text_parts = []
            curr_blocks = []

        for block in blocks:
            # Check for header/title to update section hierarchy
            if block.type in (BlockType.TITLE, BlockType.HEADER):
                # Flush previous paragraph accumulator before changing section
                flush_current_chunk()
                
                header_title = block.text.strip()
                if block.type == BlockType.TITLE:
                    current_section_path = [header_title]
                else:
                    # Header
                    if len(current_section_path) > 1:
                        current_section_path[-1] = header_title
                    else:
                        current_section_path.append(header_title)
                continue
                
            # If block is a Table, treat as an atomic, dedicated chunk (crucial for TSR fidelity)
            if block.type == BlockType.TABLE:
                flush_current_chunk()
                
                table_text = block.text
                if current_section_path:
                    table_text = f"[{' > '.join(current_section_path)}]\n{table_text}"
                    
                table_id = block.id.replace("block_table_", "")
                chunk_id = f"chunk_tbl_{doc_id}_{len(chunks)+1}_{uuid.uuid4().hex[:4]}"
                
                chunks.append(DocumentChunk(
                    chunk_id=chunk_id,
                    doc_id=doc_id,
                    text=table_text,
                    page=block.page,
                    bbox=block.bbox,
                    section_hierarchy=list(current_section_path),
                    is_table=True,
                    table_id=table_id,
                    metadata={"is_table": True, "table_id": table_id}
                ))
                continue
                
            # Check page transition
            if block.page != curr_page:
                flush_current_chunk()
                curr_page = block.page
                
            # Accumulate paragraph text
            block_tokens = self._approx_tokens(block.text)
            curr_tokens = self._approx_tokens(" ".join(curr_text_parts))
            
            if curr_tokens + block_tokens > self.max_tokens and curr_blocks:
                flush_current_chunk()
                
            curr_text_parts.append(block.text)
            curr_blocks.append(block)
            curr_page = block.page
            
        flush_current_chunk()
        return chunks
