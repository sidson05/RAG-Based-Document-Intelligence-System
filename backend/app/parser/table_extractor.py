import pdfplumber
import pandas as pd
from typing import List, Optional
import io
import uuid
from ..core.models import TableData, BoundingBox

class TableExtractor:
    """
    Dedicated Table Structure Recognition (TSR) module.
    Converts 2D visual cell structures into structured Markdown, CSV, and DataFrame
    representations (aligned with Ke et al. Tabular Data Reasoning).
    """
    
    def extract_tables_from_pdf(self, pdf_path: str) -> List[TableData]:
        tables: List[TableData] = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                page_num = page_idx + 1
                extracted_tables = page.find_tables()
                
                for table_idx, table_obj in enumerate(extracted_tables):
                    raw_data = table_obj.extract()
                    if not raw_data or len(raw_data) < 2:
                        continue
                        
                    # Clean None values in table
                    cleaned_data = []
                    for row in raw_data:
                        cleaned_row = [str(cell).strip() if cell is not None else "" for cell in row]
                        cleaned_data.append(cleaned_row)
                        
                    if not cleaned_data:
                        continue
                        
                    headers = cleaned_data[0]
                    # Ensure headers are unique and non-empty
                    safe_headers = []
                    for i, h in enumerate(headers):
                        name = h if h else f"Col_{i+1}"
                        if name in safe_headers:
                            name = f"{name}_{i}"
                        safe_headers.append(name)
                        
                    rows = cleaned_data[1:]
                    
                    # Convert to pandas DataFrame
                    df = pd.DataFrame(rows, columns=safe_headers)
                    
                    # Generate Markdown format
                    markdown_str = self._df_to_markdown(df)
                    
                    # Generate CSV format
                    csv_buf = io.StringIO()
                    df.to_csv(csv_buf, index=False)
                    csv_str = csv_buf.getvalue()
                    
                    # Bounding box in PDF points (x0, top, x1, bottom)
                    bbox_rect = table_obj.bbox
                    bbox = BoundingBox(
                        x0=float(bbox_rect[0]),
                        y0=float(bbox_rect[1]),
                        x1=float(bbox_rect[2]),
                        y1=float(bbox_rect[3]),
                        page=page_num,
                        width=float(page.width),
                        height=float(page.height)
                    )
                    
                    table_id = f"table_p{page_num}_{table_idx+1}_{uuid.uuid4().hex[:6]}"
                    
                    tables.append(TableData(
                        id=table_id,
                        page=page_num,
                        bbox=bbox,
                        markdown=markdown_str,
                        csv_str=csv_str,
                        dataframe_json=df.to_json(orient="split"),
                        num_rows=len(df),
                        num_cols=len(df.columns),
                        headers=safe_headers,
                        caption=f"Table on Page {page_num}"
                    ))
                    
        return tables

    def _df_to_markdown(self, df: pd.DataFrame) -> str:
        """Constructs clean GFM markdown table representation."""
        headers = df.columns.tolist()
        md_lines = []
        md_lines.append("| " + " | ".join(headers) + " |")
        md_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for _, row in df.iterrows():
            row_str = " | ".join([str(val).replace("\n", " ") for val in row.values])
            md_lines.append(f"| {row_str} |")
        return "\n".join(md_lines)
