from typing import List, Tuple
import re
from ..core.config import settings
from ..core.models import DocumentChunk, Citation

class Synthesizer:
    """
    Attributed QA Synthesizer (Ke et al. Reliability, Compliance & Attribution).
    
    Synthesizes answers grounded strictly in retrieved context, producing
    explicit citation references linked to document pages and coordinates.
    """
    def __init__(self):
        self._genai_client = None
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                self._genai_client = genai.Client()
            except Exception as e:
                print(f"[Synthesizer] GenAI init warning: {e}")
        
    def synthesize_answer(
        self,
        query: str,
        retrieved_chunks: List[DocumentChunk]
    ) -> Tuple[str, List[Citation]]:
        if not retrieved_chunks:
            return "No relevant information found in the ingested documents to answer the query.", []
            
        context_blocks = []
        chunk_lookup = {}
        for idx, chunk in enumerate(retrieved_chunks):
            ref_id = f"REF_{idx+1}"
            chunk_lookup[ref_id] = chunk
            page_info = f"Page {chunk.page}"
            table_info = " [TABLE]" if chunk.is_table else ""
            context_blocks.append(
                f"--- Source [{ref_id}] ({page_info}{table_info}) ---\n{chunk.text}\n"
            )
            
        context_str = "\n".join(context_blocks)
        
        prompt = f"""You are an advanced Document Intelligence Assistant.
Answer the user's question based STRICTLY and ONLY on the provided document sources below.
Do not speculate or extrapolate beyond the provided sources.

For every factual claim or data point in your answer, you MUST cite the source reference tag using square brackets, e.g. [REF_1] or [REF_2].

Provided Document Context:
{context_str}

User Question: {query}

Instructions:
1. Provide a comprehensive, accurate, and direct answer.
2. Cite all referenced facts with [REF_X].
3. If the context does not contain the answer, explicitly state that the document does not contain this information.
"""

        answer_text = ""
        if self._genai_client:
            try:
                res = self._genai_client.models.generate_content(
                    model=settings.GENERATION_MODEL,
                    contents=prompt
                )
                answer_text = res.text.strip()
            except Exception as e:
                print(f"[Synthesizer] LLM generation failed ({e}), using context extraction fallback.")

        if not answer_text:
            top_chunk = retrieved_chunks[0]
            answer_text = f"Based on [REF_1] (Page {top_chunk.page}):\n\n{top_chunk.text}"

        cited_refs = set(re.findall(r"\[REF_(\d+)\]", answer_text))
        citations: List[Citation] = []
        for ref_num in sorted(cited_refs, key=int):
            ref_key = f"REF_{ref_num}"
            if ref_key in chunk_lookup:
                c = chunk_lookup[ref_key]
                citations.append(Citation(
                    chunk_id=c.chunk_id,
                    doc_id=c.doc_id,
                    page=c.page,
                    bbox=c.bbox,
                    quoted_snippet=c.text[:200] + ("..." if len(c.text) > 200 else "")
                ))
                
        if not citations and retrieved_chunks:
            top_c = retrieved_chunks[0]
            citations.append(Citation(
                chunk_id=top_c.chunk_id,
                doc_id=top_c.doc_id,
                page=top_c.page,
                bbox=top_c.bbox,
                quoted_snippet=top_c.text[:200] + ("..." if len(top_c.text) > 200 else "")
            ))
            
        return answer_text, citations

synthesizer = Synthesizer()
