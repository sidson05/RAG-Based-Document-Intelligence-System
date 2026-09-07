import shutil
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ..core.config import settings
from ..core.models import DocumentMetadata, AgentQueryResponse, Citation, BoundingBox
from ..parser.layout_parser import LayoutParser
from ..parser.vision_renderer import VisionRenderer
from ..indexer.chunker import HierarchicalChunker
from ..indexer.hybrid_store import hybrid_store
from ..agent.orchestrator import document_agent

router = APIRouter()
layout_parser = LayoutParser()
vision_renderer = VisionRenderer()
chunker = HierarchicalChunker(max_tokens=settings.MAX_CHUNK_TOKENS)

class QueryRequest(BaseModel):
    query: str
    doc_id: Optional[str] = None

class HighlightRequest(BaseModel):
    bbox: BoundingBox

@router.post("/upload", response_model=DocumentMetadata)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF documents are currently supported.")
        
    doc_id = f"doc_{uuid.uuid4().hex[:8]}"
    file_path = settings.UPLOAD_DIR / f"{doc_id}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file_size = file_path.stat().st_size
    
    # 1. Parse document layout and extract tables
    blocks, tables = layout_parser.parse_pdf(str(file_path))
    
    # 2. Render and cache page images
    page_paths = vision_renderer.render_all_pages(str(file_path))
    num_pages = len(page_paths)
    
    # 3. Structure-aware chunking
    chunks = chunker.chunk_document(doc_id=doc_id, blocks=blocks, tables=tables)
    
    # 4. Metadata
    metadata = DocumentMetadata(
        doc_id=doc_id,
        filename=file.filename,
        file_path=str(file_path),
        file_size_bytes=file_size,
        num_pages=num_pages,
        num_blocks=len(blocks),
        num_tables=len(tables),
        num_chunks=len(chunks)
    )
    
    # 5. Hybrid indexing (dense FAISS + sparse BM25)
    hybrid_store.add_document(metadata, chunks, tables)
    
    return metadata

@router.post("/query", response_model=AgentQueryResponse)
async def query_document(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    response = document_agent.process_query(
        query=request.query,
        doc_id_filter=request.doc_id
    )
    return response

@router.get("/documents", response_model=List[DocumentMetadata])
async def list_documents():
    return list(hybrid_store.documents.values())

@router.get("/documents/{doc_id}", response_model=DocumentMetadata)
async def get_document(doc_id: str):
    doc = hybrid_store.documents.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return doc

@router.get("/documents/{doc_id}/pages/{page_num}")
async def get_page_image(doc_id: str, page_num: int):
    doc = hybrid_store.documents.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    try:
        img_path = vision_renderer.render_page(doc.file_path, page_num)
        return FileResponse(str(img_path), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/documents/{doc_id}/highlight")
async def get_highlighted_page(doc_id: str, req: HighlightRequest):
    doc = hybrid_store.documents.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    try:
        highlighted_path = vision_renderer.create_highlighted_page(
            doc_path=doc.file_path,
            bbox=req.bbox
        )
        return FileResponse(str(highlighted_path), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
