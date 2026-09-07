import pymupdf as fitz
from pathlib import Path
from PIL import Image, ImageDraw
import io
from typing import Optional, Tuple
from ..core.config import settings
from ..core.models import BoundingBox

class VisionRenderer:
    """
    Renders PDF pages to high-resolution images and generates
    visual crops or highlighted bounding-box overlays for visual grounding
    (aligned with Ke et al. End-to-End & Multimodal Paradigm).
    """
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or settings.PAGE_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def render_page(self, doc_path: str, page_number: int, dpi: int = 150) -> Path:
        """
        Renders a given page (1-indexed) to a PNG file and caches it.
        """
        doc_filename = Path(doc_path).stem
        output_filename = f"{doc_filename}_page_{page_number}.png"
        output_path = self.cache_dir / output_filename
        
        if output_path.exists():
            return output_path
            
        doc = fitz.open(doc_path)
        if page_number < 1 or page_number > len(doc):
            doc.close()
            raise ValueError(f"Page number {page_number} out of range (1 to {len(doc)})")
            
        page = doc[page_number - 1]
        pix = page.get_pixmap(dpi=dpi)
        pix.save(str(output_path))
        doc.close()
        return output_path

    def render_all_pages(self, doc_path: str, dpi: int = 150) -> list[Path]:
        """
        Renders all pages of a document and returns paths to cached images.
        """
        doc = fitz.open(doc_path)
        total_pages = len(doc)
        doc.close()
        return [self.render_page(doc_path, p, dpi=dpi) for p in range(1, total_pages + 1)]

    def create_highlighted_page(
        self,
        doc_path: str,
        bbox: BoundingBox,
        highlight_color: Tuple[int, int, int, int] = (255, 230, 0, 90),
        border_color: Tuple[int, int, int, int] = (230, 100, 0, 255),
        dpi: int = 150
    ) -> Path:
        """
        Renders page with a highlighted bounding box overlay for citation verification.
        """
        page_img_path = self.render_page(doc_path, bbox.page, dpi=dpi)
        base_img = Image.open(page_img_path).convert("RGBA")
        
        # Determine scaling between PDF points and rendered image pixels
        doc = fitz.open(doc_path)
        pdf_page = doc[bbox.page - 1]
        pdf_rect = pdf_page.rect
        doc.close()
        
        scale_x = base_img.width / pdf_rect.width
        scale_y = base_img.height / pdf_rect.height
        
        # Scale coordinates
        x0 = bbox.x0 * scale_x
        y0 = bbox.y0 * scale_y
        x1 = bbox.x1 * scale_x
        y1 = bbox.y1 * scale_y
        
        # Draw translucent overlay
        overlay = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        draw.rectangle([x0, y0, x1, y1], fill=highlight_color, outline=border_color, width=3)
        
        highlighted = Image.alpha_composite(base_img, overlay)
        
        doc_filename = Path(doc_path).stem
        out_name = f"{doc_filename}_highlight_p{bbox.page}_{int(x0)}_{int(y0)}.png"
        out_path = self.cache_dir / out_name
        highlighted.convert("RGB").save(str(out_path))
        return out_path

    def crop_bounding_box(self, doc_path: str, bbox: BoundingBox, dpi: int = 150) -> Image.Image:
        """
        Crops the exact region defined by bbox for multimodal VLM visual inspection.
        """
        page_img_path = self.render_page(doc_path, bbox.page, dpi=dpi)
        img = Image.open(page_img_path)
        
        doc = fitz.open(doc_path)
        pdf_page = doc[bbox.page - 1]
        pdf_rect = pdf_page.rect
        doc.close()
        
        scale_x = img.width / pdf_rect.width
        scale_y = img.height / pdf_rect.height
        
        # Add slight padding
        pad = 5
        x0 = max(0, int(bbox.x0 * scale_x) - pad)
        y0 = max(0, int(bbox.y0 * scale_y) - pad)
        x1 = min(img.width, int(bbox.x1 * scale_x) + pad)
        y1 = min(img.height, int(bbox.y1 * scale_y) + pad)
        
        return img.crop((x0, y0, x1, y1))
