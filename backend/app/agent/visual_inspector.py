from pathlib import Path
from PIL import Image
from typing import Optional
from ..core.config import settings
from ..core.models import BoundingBox
from ..parser.vision_renderer import VisionRenderer

class VisualInspector:
    """
    Multimodal Vision-Language Model (VLM) Inspector
    (Ke et al. End-to-End Multimodal Paradigm).
    """
    def __init__(self):
        self.renderer = VisionRenderer()
        self._genai_client = None
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                self._genai_client = genai.Client()
            except Exception as e:
                print(f"[VisualInspector] GenAI init warning: {e}")
        
    def inspect_visual_region(
        self,
        doc_path: str,
        page_num: int,
        query: str,
        bbox: Optional[BoundingBox] = None
    ) -> str:
        if bbox is not None:
            img = self.renderer.crop_bounding_box(doc_path, bbox)
        else:
            page_img_path = self.renderer.render_page(doc_path, page_num)
            img = Image.open(page_img_path)
            
        if not self._genai_client:
            return f"[Visual Inspector] Visual inspection requested for Page {page_num}, but GEMINI_API_KEY is not configured."
            
        try:
            prompt = (
                f"You are a Document Visual Question Answering (DocVQA) expert.\n"
                f"Analyze this document image snippet from Page {page_num} carefully.\n"
                f"Question: {query}\n\n"
                f"Provide a precise, factual answer based strictly on visual evidence in the image."
            )
            
            res = self._genai_client.models.generate_content(
                model=settings.VISION_MODEL,
                contents=[img, prompt]
            )
            return res.text.strip()
        except Exception as e:
            return f"[Visual Inspector] Error inspecting visual region: {str(e)}"

visual_inspector = VisualInspector()
