from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class BlockType(str, Enum):
    TITLE = "title"
    HEADER = "header"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    FIGURE = "figure"
    CAPTION = "caption"
    LIST_ITEM = "list_item"
    FOOTER = "footer"

class BoundingBox(BaseModel):
    """Normalized or absolute coordinates: x0, y0, x1, y1 (top-left to bottom-right)"""
    x0: float
    y0: float
    x1: float
    y1: float
    page: int
    width: Optional[float] = None
    height: Optional[float] = None

class LayoutBlock(BaseModel):
    id: str
    type: BlockType
    text: str
    bbox: BoundingBox
    page: int
    reading_order: int
    font_size: Optional[float] = None
    is_bold: Optional[bool] = False

class TableData(BaseModel):
    id: str
    page: int
    bbox: BoundingBox
    markdown: str
    csv_str: str
    dataframe_json: Optional[str] = None
    num_rows: int
    num_cols: int
    headers: List[str] = Field(default_factory=list)
    caption: Optional[str] = None

class DocumentChunk(BaseModel):
    chunk_id: str
    doc_id: str
    text: str
    page: int
    bbox: BoundingBox
    section_hierarchy: List[str] = Field(default_factory=list)
    is_table: bool = False
    table_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Citation(BaseModel):
    chunk_id: str
    doc_id: str
    page: int
    bbox: BoundingBox
    quoted_snippet: str
    source_title: Optional[str] = None

class RetrievalResult(BaseModel):
    chunk: DocumentChunk
    dense_score: float = 0.0
    sparse_score: float = 0.0
    rrf_score: float = 0.0
    rerank_score: float = 0.0

class QueryRoute(str, Enum):
    DIRECT_TEXT = "direct_text"
    TABLE_CALCULATION = "table_calculation"
    VISUAL_INSPECTION = "visual_inspection"
    MULTI_HOP_REASONING = "multi_hop_reasoning"

class AgentQueryResponse(BaseModel):
    query: str
    answer: str
    route_taken: QueryRoute
    citations: List[Citation] = Field(default_factory=list)
    calculation_code: Optional[str] = None
    calculation_result: Optional[str] = None
    verification_passed: bool = True
    verification_notes: Optional[str] = None
    reasoning_steps: List[str] = Field(default_factory=list)
    retrieved_chunks: List[DocumentChunk] = Field(default_factory=list)

class DocumentMetadata(BaseModel):
    doc_id: str
    filename: str
    file_path: str
    file_size_bytes: int
    num_pages: int
    num_blocks: int
    num_tables: int
    num_chunks: int
    upload_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
