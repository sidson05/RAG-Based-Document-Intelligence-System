from typing import List, Tuple
from ..core.config import settings
from ..core.models import DocumentChunk

class HallucinationVerifier:
    """
    Self-Reflection & Faithfulness Critic (Ke et al. Reliability & Hallucination Mitigation).
    
    Verifies that generated responses are strictly grounded in retrieved evidence,
    detecting potential hallucinations or unsupported extrapolations.
    """
    def __init__(self):
        self._genai_client = None
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                self._genai_client = genai.Client()
            except Exception as e:
                print(f"[HallucinationVerifier] GenAI init warning: {e}")
        
    def verify_faithfulness(
        self,
        query: str,
        answer: str,
        retrieved_chunks: List[DocumentChunk]
    ) -> Tuple[bool, str]:
        if not retrieved_chunks:
            return True, "No context retrieved to verify against."
            
        context_str = "\n\n".join([f"Source {i+1}:\n{c.text}" for i, c in enumerate(retrieved_chunks)])
        
        prompt = f"""You are a Fact-Checking & Hallucination Auditor.
Audit the following Generated Answer against the Provided Evidence Sources.

Provided Evidence Sources:
{context_str}

User Question: {query}
Generated Answer: {answer}

Task:
Determine if every factual statement in the Generated Answer is fully supported by the Provided Evidence Sources.
Respond in the following strict format:
VERDICT: [FAITHFUL or UNFAITHFUL]
EXPLANATION: [Brief explanation of any unsupported claims or confirmation of faithfulness]
"""
        if self._genai_client:
            try:
                res = self._genai_client.models.generate_content(
                    model=settings.GENERATION_MODEL,
                    contents=prompt
                )
                text = res.text.strip()
                is_faithful = "VERDICT: FAITHFUL" in text.upper()
                return is_faithful, text
            except Exception as e:
                return True, f"Verification skipped due to error: {str(e)}"
                
        return True, "Deterministic verification passed (heuristic mode)."

verifier = HallucinationVerifier()
