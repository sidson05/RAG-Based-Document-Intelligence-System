import fitz  # PyMuPDF
from pathlib import Path

def create_benchmark_pdf(output_path: str):
    """
    Generates a rich benchmark PDF with:
    - Page 1: Academic research paper format (Title, Abstract, Multi-column Layout, Headings)
    - Page 2: Structured financial performance table (Quarter, Revenue, Expenses, Net Profit)
    - Page 3: Summary, bullet points, and visual test block
    """
    doc = fitz.open()
    
    # --- PAGE 1: Academic Layout ---
    page1 = doc.new_page(width=595, height=842)  # A4 size
    # Title
    page1.insert_text(fitz.Point(50, 60), "Large Language Models in Document Intelligence: Survey", fontsize=16, fontname="helv", color=(0, 0, 0))
    # Authors
    page1.insert_text(fitz.Point(50, 85), "Wenjun Ke, Yifan Zheng, Yining Li, Dong Nie, Yao He", fontsize=10, fontname="helv", color=(0.3, 0.3, 0.3))
    # Section 1
    page1.insert_text(fitz.Point(50, 120), "1. Introduction", fontsize=13, fontname="helv", color=(0.1, 0.1, 0.5))
    intro_text = (
        "Document intelligence focuses on the automatic extraction, understanding, and analysis "
        "of business documents. Recent advances in Large Language Models (LLMs) and Vision-Language "
        "Models (VLMs) have reshaped traditional document analysis workflows into unified reasoning "
        "pipelines. In this survey, we examine over 300 research publications between 2021 and 2025."
    )
    rect_intro = fitz.Rect(50, 130, 545, 190)
    page1.insert_textbox(rect_intro, intro_text, fontsize=10, fontname="helv")
    
    # Section 2
    page1.insert_text(fitz.Point(50, 220), "2. Architectural Paradigms", fontsize=13, fontname="helv", color=(0.1, 0.1, 0.5))
    para_text = (
        "Modern systems are categorized into pipeline-based approaches and end-to-end multimodal "
        "architectures. Pipeline systems decompose tasks into Document Layout Analysis (DLA), "
        "Table Structure Recognition (TSR), and Optical Character Recognition (OCR), followed by "
        "Retrieval-Augmented Generation (RAG). Meanwhile, multimodal LLMs process document page images "
        "directly, preserving non-linear reading order and spatial visual structures."
    )
    rect_para = fitz.Rect(50, 235, 545, 310)
    page1.insert_textbox(rect_para, para_text, fontsize=10, fontname="helv")
    
    # Page number
    page1.insert_text(fitz.Point(280, 810), "Page 1", fontsize=9, fontname="helv", color=(0.5, 0.5, 0.5))
    
    # --- PAGE 2: Structured Financial Table ---
    page2 = doc.new_page(width=595, height=842)
    page2.insert_text(fitz.Point(50, 60), "3. Empirical Performance and Evaluation", fontsize=14, fontname="helv", color=(0.1, 0.1, 0.5))
    page2.insert_text(fitz.Point(50, 85), "Table 1: Quarterly Financial and Metric Comparison (Fiscal Year 2025)", fontsize=11, fontname="helv")
    
    # Draw table grid and content
    # Headers
    headers = ["Quarter", "Revenue ($M)", "Expenses ($M)", "Net Profit ($M)", "Accuracy (%)"]
    col_widths = [80, 100, 100, 100, 100]
    start_x = 50
    start_y = 110
    row_h = 25
    
    table_rows = [
        ["Q1-2025", "120.5", "85.2", "35.3", "92.4"],
        ["Q2-2025", "145.0", "92.0", "53.0", "94.8"],
        ["Q3-2025", "180.2", "105.1", "75.1", "96.2"],
        ["Q4-2025", "210.0", "118.5", "91.5", "97.5"],
    ]
    
    # Draw Header row
    curr_x = start_x
    for i, h in enumerate(headers):
        rect = fitz.Rect(curr_x, start_y, curr_x + col_widths[i], start_y + row_h)
        page2.draw_rect(rect, color=(0.2, 0.2, 0.2), fill=(0.9, 0.9, 0.95))
        page2.insert_text(fitz.Point(curr_x + 8, start_y + 16), h, fontsize=9, fontname="helv", color=(0, 0, 0))
        curr_x += col_widths[i]
        
    # Draw Data rows
    curr_y = start_y + row_h
    for r_idx, row in enumerate(table_rows):
        curr_x = start_x
        for c_idx, cell in enumerate(row):
            rect = fitz.Rect(curr_x, curr_y, curr_x + col_widths[c_idx], curr_y + row_h)
            page2.draw_rect(rect, color=(0.7, 0.7, 0.7))
            page2.insert_text(fitz.Point(curr_x + 8, curr_y + 16), cell, fontsize=9, fontname="helv", color=(0.1, 0.1, 0.1))
            curr_x += col_widths[c_idx]
        curr_y += row_h
        
    # Commentary below table
    note_rect = fitz.Rect(50, curr_y + 30, 545, curr_y + 100)
    page2.insert_textbox(
        note_rect,
        "Observations from Table 1 demonstrate consistent quarter-over-quarter revenue expansion, "
        "rising from $120.5M in Q1 to $210.0M in Q4. Net profit grew by $56.2M across the full year, "
        "with document extraction accuracy reaching an optimal 97.5% in Q4.",
        fontsize=10, fontname="helv"
    )
    
    page2.insert_text(fitz.Point(280, 810), "Page 2", fontsize=9, fontname="helv", color=(0.5, 0.5, 0.5))

    # --- PAGE 3: Visual & Concluding Section ---
    page3 = doc.new_page(width=595, height=842)
    page3.insert_text(fitz.Point(50, 60), "4. Future Challenges and Conclusions", fontsize=14, fontname="helv", color=(0.1, 0.1, 0.5))
    
    concl_text = (
        "Key remaining challenges include handling ultra-long context documents, maintaining high-fidelity "
        "spatial alignment for complex non-standard templates, and preventing hallucination in high-stakes "
        "financial and regulatory domains. The integration of deterministic tool verification with multimodal "
        "LLMs marks a decisive step toward trustworthy enterprise document intelligence."
    )
    page3.insert_textbox(fitz.Rect(50, 80, 545, 160), concl_text, fontsize=10, fontname="helv")
    
    # Draw a visual badge/figure container
    fig_rect = fitz.Rect(50, 180, 300, 280)
    page3.draw_rect(fig_rect, color=(0.2, 0.4, 0.8), fill=(0.93, 0.96, 1.0), width=2)
    page3.insert_text(fitz.Point(65, 210), "Figure 1: Verified Document Seal", fontsize=11, fontname="helv", color=(0.1, 0.2, 0.6))
    page3.insert_text(fitz.Point(65, 235), "Status: System Verified Compliance", fontsize=9, fontname="helv", color=(0.2, 0.5, 0.2))
    page3.insert_text(fitz.Point(65, 255), "Security ID: #DOC-2026-X99", fontsize=9, fontname="helv", color=(0.4, 0.4, 0.4))
    
    page3.insert_text(fitz.Point(280, 810), "Page 3", fontsize=9, fontname="helv", color=(0.5, 0.5, 0.5))
    
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_p))
    doc.close()
    print(f"Created benchmark document at: {out_p}")
    return str(out_p)

if __name__ == "__main__":
    create_benchmark_pdf("data/sample_docs/benchmark_paper.pdf")
