from typing import Optional, List
from ..core.models import (
    AgentQueryResponse,
    QueryRoute,
    Citation,
    DocumentChunk,
    RetrievalResult
)
from ..core.config import settings
from ..retriever.hybrid_retriever import hybrid_retriever
from ..indexer.hybrid_store import hybrid_store
from .router import query_router
from .code_interpreter import code_interpreter
from .visual_inspector import visual_inspector
from .synthesizer import synthesizer
from .verifier import verifier

class DocumentAgentOrchestrator:
    """
    Agentic Orchestrator for Document Intelligence
    (Ke et al. Unified Document Intelligence Paradigm).
    """
    
    def process_query(
        self,
        query: str,
        doc_id_filter: Optional[str] = None
    ) -> AgentQueryResponse:
        reasoning_steps: List[str] = []
        
        # Step 1: Initial Hybrid Retrieval
        reasoning_steps.append("Executing hybrid dense (FAISS) + sparse (BM25) search with RRF.")
        retrieval_results: List[RetrievalResult] = hybrid_retriever.retrieve(
            query=query,
            top_k=settings.TOP_K_RETRIEVAL,
            rerank_top_n=settings.RERANK_TOP_N,
            doc_id_filter=doc_id_filter
        )
        
        retrieved_chunks = [r.chunk for r in retrieval_results]
        has_table = any(c.is_table for c in retrieved_chunks)
        
        # Step 2: Route Classification
        route = query_router.route_query(query, has_table_context=has_table)
        reasoning_steps.append(f"Intent classified: Routed to {route.value.upper()}.")
        
        citations: List[Citation] = []
        calc_code = None
        calc_result = None
        
        # Step 3: Branch by Route
        if route == QueryRoute.TABLE_CALCULATION and has_table:
            # Find the most relevant table
            table_chunk = next(c for c in retrieved_chunks if c.is_table)
            table_data = hybrid_store.get_table_by_id(table_chunk.table_id) if table_chunk.table_id else None
            
            if table_data:
                reasoning_steps.append(f"Table found on Page {table_data.page}. Generating & executing Python/Pandas calculation.")
                calc_code, calc_result, answer = code_interpreter.generate_and_execute(query, table_data)
                citations.append(Citation(
                    chunk_id=table_chunk.chunk_id,
                    doc_id=table_chunk.doc_id,
                    page=table_data.page,
                    bbox=table_data.bbox,
                    quoted_snippet=f"Table ({table_data.num_rows}x{table_data.num_cols}): {', '.join(table_data.headers[:4])}..."
                ))
            else:
                # Table metadata missing, synthesize directly
                reasoning_steps.append("Table metadata fallback: synthesizing with direct QA.")
                answer, citations = synthesizer.synthesize_answer(query, retrieved_chunks)
                
        elif route == QueryRoute.VISUAL_INSPECTION and retrieved_chunks:
            top_c = retrieved_chunks[0]
            doc_meta = hybrid_store.documents.get(top_c.doc_id)
            if doc_meta:
                reasoning_steps.append(f"Invoking Multimodal VLM Inspector for Page {top_c.page}.")
                vlm_answer = visual_inspector.inspect_visual_region(
                    doc_path=doc_meta.file_path,
                    page_num=top_c.page,
                    query=query,
                    bbox=top_c.bbox
                )
                answer = f"**Visual Inspection Analysis (Page {top_c.page}):**\n\n{vlm_answer}"
                citations.append(Citation(
                    chunk_id=top_c.chunk_id,
                    doc_id=top_c.doc_id,
                    page=top_c.page,
                    bbox=top_c.bbox,
                    quoted_snippet="Visual region analyzed directly via VLM."
                ))
            else:
                answer, citations = synthesizer.synthesize_answer(query, retrieved_chunks)
                
        else:
            # Direct Text or Multi-Hop Reasoning
            reasoning_steps.append("Synthesizing answer with strict attribution & bracketed citations.")
            answer, citations = synthesizer.synthesize_answer(query, retrieved_chunks)
            
        # Step 4: Verification & Hallucination Audit
        reasoning_steps.append("Running Hallucination & Faithfulness Critic.")
        is_faithful, verification_notes = verifier.verify_faithfulness(query, answer, retrieved_chunks)
        
        return AgentQueryResponse(
            query=query,
            answer=answer,
            route_taken=route,
            citations=citations,
            calculation_code=calc_code,
            calculation_result=calc_result,
            verification_passed=is_faithful,
            verification_notes=verification_notes,
            reasoning_steps=reasoning_steps,
            retrieved_chunks=retrieved_chunks
        )

document_agent = DocumentAgentOrchestrator()
