import io
import time
import base64
import html
import re
from typing import Optional, List, Dict, Any
import requests
from PIL import Image, ImageDraw
import streamlit as st

try:
    from frontend.styles import load_css
except ImportError:
    from styles import load_css

# Page Configuration
st.set_page_config(
    layout="wide",
    page_title="DocIntel",
    page_icon="📄",
    initial_sidebar_state="expanded"
)

# Inject Executive Light Theme CSS
st.markdown(f"<style>{load_css()}</style>", unsafe_allow_html=True)

BACKEND_URL = "http://127.0.0.1:8000/api"

# State Management Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_doc_id" not in st.session_state:
    st.session_state.selected_doc_id = None
if "current_page" not in st.session_state:
    st.session_state.current_page = 1
if "active_ref" not in st.session_state:
    st.session_state.active_ref = None
if "active_citation" not in st.session_state:
    st.session_state.active_citation = None
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# Query Parameter handling for inline citation clicks without triggering an LLM call
if "ref" in st.query_params:
    try:
        ref_num = int(st.query_params["ref"])
        st.session_state.active_ref = ref_num
        for msg in reversed(st.session_state.messages):
            if msg.get("role") == "assistant" and msg.get("citations"):
                cites = msg["citations"]
                if 1 <= ref_num <= len(cites):
                    target_cite = cites[ref_num - 1]
                    st.session_state.active_citation = target_cite
                    st.session_state.current_page = target_cite.get("page", 1)
                    break
    except Exception:
        pass


def fetch_documents() -> List[Dict[str, Any]]:
    try:
        r = requests.get(f"{BACKEND_URL}/documents", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return []
    return []


def format_file_size(size_bytes: int) -> str:
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / 1024:.0f} KB"


def format_route_name(route_str: str) -> str:
    r = route_str.lower()
    if "calc" in r:
        return "CODE_INTERPRETER"
    elif "vis" in r or "vlm" in r:
        return "VLM"
    elif "multi" in r:
        return "MULTI_HOP"
    return "DIRECT_TEXT"


def draw_sand_highlight(img_bytes: bytes, bbox: dict) -> bytes:
    """
    Overlays a 1.5px --sand (#d9a441) border with a translucent sand fill
    (rgba(217, 164, 65, 0.16)) and radius 4px on the base page image.
    """
    try:
        base_img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
        page_w = bbox.get("width") or 612.0
        page_h = bbox.get("height") or 792.0
        scale_x = base_img.width / page_w
        scale_y = base_img.height / page_h

        x0 = bbox.get("x0", 0.0) * scale_x
        y0 = bbox.get("y0", 0.0) * scale_y
        x1 = bbox.get("x1", 0.0) * scale_x
        y1 = bbox.get("y1", 0.0) * scale_y

        overlay = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        sand_fill = (217, 164, 65, int(255 * 0.16))
        sand_border = (217, 164, 65, 255)

        if hasattr(draw, "rounded_rectangle"):
            draw.rounded_rectangle([x0, y0, x1, y1], radius=4, fill=sand_fill, outline=sand_border, width=2)
        else:
            draw.rectangle([x0, y0, x1, y1], fill=sand_fill, outline=sand_border, width=2)

        highlighted = Image.alpha_composite(base_img, overlay)
        buf = io.BytesIO()
        highlighted.convert("RGB").save(buf, format="PNG")
        return buf.getvalue()
    except Exception:
        return img_bytes


def linkify_citations(text: str, active_ref: Optional[int]) -> str:
    """
    Converts bracketed citations like [REF_1] into clickable chips with query params.
    """
    def repl(m):
        r_num = int(m.group(1))
        active_cls = " active" if active_ref == r_num else ""
        return f'<a href="?ref={r_num}" target="_self" class="ref-chip{active_cls}">REF_{r_num}</a>'
    return re.sub(r'\[REF_(\d+)\]', repl, text)


# ==========================================
# 1. SIDEBAR RENDERING
# ==========================================
def render_sidebar(docs: List[Dict[str, Any]]):
    with st.sidebar:
        # Brand Block
        st.markdown("""
        <div class="brand-block">
            <div class="brand-tile">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
            </div>
            <div>
                <div class="brand-name">DocIntel</div>
                <div class="brand-sub">Document intelligence</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Section Label: DOCUMENT INGESTION
        st.markdown('<div class="section-label">DOCUMENT INGESTION</div>', unsafe_allow_html=True)
        st.markdown('<div class="helper-text">Layout-aware parsing, table structure recognition and visual rendering.</div>', unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Upload PDF Document",
            type=["pdf"],
            help="Limit 200 MB, PDF only",
            label_visibility="collapsed"
        )

        if uploaded_file is not None:
            # Compact File Chip
            st.markdown(f"""
            <div class="file-chip">
                <div class="file-chip-icon">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                    </svg>
                </div>
                <div class="file-chip-info">
                    <div class="file-chip-name">{html.escape(uploaded_file.name)}</div>
                    <div class="file-chip-size">{format_file_size(uploaded_file.size)}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Primary button "Process & index"
            if st.button("Process & index", key="btn_process_index", use_container_width=True, type="primary"):
                checklist_placeholder = st.empty()

                def update_checklist(active_idx: int, done: bool = False):
                    steps = [
                        "Layout analysis",
                        "Table recognition",
                        "Structure-aware chunking",
                        "FAISS + BM25 index"
                    ]
                    items = []
                    for idx, name in enumerate(steps, 1):
                        if done or idx < active_idx:
                            icon = '<span class="check-circle">✓</span>'
                        elif idx == active_idx:
                            icon = '<span class="thinking-dot"></span>'
                        else:
                            icon = '<span class="check-pending"></span>'
                        items.append(f'<div class="checklist-item">{icon}<span>{name}</span></div>')
                    checklist_placeholder.markdown(f'<div class="checklist-box">{"".join(items)}</div>', unsafe_allow_html=True)

                update_checklist(1)
                time.sleep(0.3)
                update_checklist(2)

                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                try:
                    update_checklist(3)
                    res = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=90)
                    if res.status_code == 200:
                        update_checklist(4, done=True)
                        meta = res.json()
                        st.session_state.selected_doc_id = meta["doc_id"]
                        st.session_state.current_page = 1
                        st.session_state.active_ref = None
                        st.session_state.active_citation = None
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.markdown(f'<div class="inline-error">Upload failed: {html.escape(res.text)}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f'<div class="inline-error">Connection error: {html.escape(str(e))}</div>', unsafe_allow_html=True)

        st.markdown("<hr style='border:none; border-top:1px solid var(--line); margin: 18px 0;'>", unsafe_allow_html=True)

        # Section Label: INDEXED DOCUMENTS
        st.markdown('<div class="section-label">INDEXED DOCUMENTS</div>', unsafe_allow_html=True)

        if docs:
            doc_options = {
                d["doc_id"]: f"{d['filename']} · {d['num_pages']} pg, {d['num_tables']} tbls"
                for d in docs
            }
            curr_id = st.session_state.selected_doc_id or list(doc_options.keys())[0]
            default_index = list(doc_options.keys()).index(curr_id) if curr_id in doc_options else 0

            selected_id = st.selectbox(
                "Active document",
                options=list(doc_options.keys()),
                format_func=lambda x: doc_options[x],
                index=default_index,
                key="select_active_doc",
                label_visibility="visible"
            )
            if selected_id != st.session_state.selected_doc_id:
                st.session_state.selected_doc_id = selected_id
                st.session_state.current_page = 1
                st.session_state.active_ref = None
                st.session_state.active_citation = None
                st.rerun()

            selected_meta = next((d for d in docs if d["doc_id"] == selected_id), None)
            if selected_meta:
                with st.expander("Document metadata & metrics", expanded=False):
                    st.markdown(f"""
                    <div class="metrics-grid">
                        <div class="metric-k">Pages</div><div class="metric-v">{selected_meta.get('num_pages', 0)}</div>
                        <div class="metric-k">Tables detected</div><div class="metric-v">{selected_meta.get('num_tables', 0)}</div>
                        <div class="metric-k">Indexed chunks</div><div class="metric-v">{selected_meta.get('num_chunks', 0)}</div>
                        <div class="metric-k">Layout blocks</div><div class="metric-v">{selected_meta.get('num_blocks', 0)}</div>
                        <div class="metric-k">Retrieval</div><div class="metric-v">FAISS + BM25</div>
                        <div class="metric-k">Fusion</div><div class="metric-v">RRF (k=60)</div>
                        <div class="metric-k">Reranker</div><div class="metric-v">MiniLM-L6-v2</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="helper-text">No documents indexed yet. Upload a PDF above to begin.</div>', unsafe_allow_html=True)


# ==========================================
# 2. MAIN HEADER RENDERING
# ==========================================
def render_header():
    st.markdown('<div class="paper-badge">ACM TOIS 2026 · Survey-aligned architecture · DOI 10.1145/3768156</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">RAG-Based Document Intelligent System</h1>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Unified Hybrid RAG Architecture: Layout-Aware Parsing, Tabular Code Interpreter, Visual Grounding & Hallucination Auditor</div>', unsafe_allow_html=True)

    # Pipeline strip with 5 pills and 6px sage dots
    st.markdown("""
    <div class="pipeline-strip">
        <div class="pipeline-pill"><span class="sage-dot"></span>Layout & table parsing</div>
        <div class="pipeline-pill"><span class="sage-dot"></span>Hybrid dense + sparse retrieval</div>
        <div class="pipeline-pill"><span class="sage-dot"></span>Cross-encoder rerank</div>
        <div class="pipeline-pill"><span class="sage-dot"></span>Agentic tools</div>
        <div class="pipeline-pill"><span class="sage-dot"></span>Faithfulness audit</div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# 3. INTELLIGENT ASSISTANT (LEFT CARD)
# ==========================================
def render_chat(docs: List[Dict[str, Any]]):
    with st.container(border=True):
        # Card Header
        st.markdown("""
        <div class="card-header-bar">
            <span class="card-title">Intelligent assistant</span>
            <span class="card-model-tag">gemini-3.6-flash</span>
        </div>
        """, unsafe_allow_html=True)

        # Check for incoming pending query
        active_query = st.session_state.get("pending_query")
        st.session_state.pending_query = None
        if active_query:
            if not st.session_state.selected_doc_id and docs:
                st.session_state.selected_doc_id = docs[0]["doc_id"]
            st.session_state.messages.append({"role": "user", "content": active_query})
            st.session_state.is_querying = True
        else:
            st.session_state.is_querying = False

        # Scrollable Conversation Container (height=520)
        with st.container(height=520):
            if not st.session_state.messages:
                st.markdown("""
                <div class="empty-card" style="margin-top: 60px;">
                    <div class="empty-card-icon">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                        </svg>
                    </div>
                    <div class="empty-card-text">Ask a question about the active document, query tabular figures, or verify citations.</div>
                </div>
                """, unsafe_allow_html=True)

            for msg_idx, msg in enumerate(st.session_state.messages):
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-bubble-user">
                        <div class="user-pill">{html.escape(msg['content'])}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Assistant Message
                    route_display = format_route_name(msg.get("route", "direct_text"))
                    is_verified = msg.get("verification_passed", True)
                    ver_html = (
                        '<span class="tag-verified">✓ Verified faithful</span>'
                        if is_verified
                        else '<span class="tag-unverified">No evidence found</span>'
                    )

                    citations = msg.get("citations", [])
                    raw_content = msg.get("content", "")
                    linked_content = linkify_citations(raw_content, st.session_state.get("active_ref"))

                    code_block_html = ""
                    if msg.get("calc_code"):
                        code_esc = html.escape(msg["calc_code"])
                        res_str = html.escape(str(msg.get("calc_result", "")))
                        code_block_html = f"""
                        <div class="code-block-box">
                            <div class="code-block-header">CODE INTERPRETER · PYTHON EXECUTION</div>
                            <pre class="code-block-code"><code>{code_esc}</code></pre>
                            <div class="code-block-result">Result: {res_str}</div>
                        </div>
                        """

                    latency = msg.get("latency", 0.7)
                    footer_html = f'<div class="msg-footer">{len(citations)} sources · reranked · {latency:.1f} s</div>'

                    # Header with avatar and tags
                    st.markdown(f"""
                    <div class="chat-row-assistant" style="margin-bottom: 4px;">
                        <div class="assistant-avatar">AI</div>
                        <div class="assistant-body">
                            <div class="tags-row">
                                <span class="tag-route">Route: {route_display}</span>
                                {ver_html}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if code_block_html:
                        st.markdown(code_block_html, unsafe_allow_html=True)

                    st.markdown(f'<div style="padding-left: 42px;" class="answer-text">{linked_content}</div>', unsafe_allow_html=True)

                    # Interactive Citation Chips
                    if citations:
                        st.markdown('<div style="height: 4px;"></div>', unsafe_allow_html=True)
                        chip_cols = st.columns(min(len(citations), 4))
                        for i, cite in enumerate(citations):
                            col_idx = i % len(chip_cols)
                            with chip_cols[col_idx]:
                                is_chip_active = (st.session_state.get("active_ref") == (i + 1))
                                btn_kind = "primary" if is_chip_active else "secondary"
                                p = cite.get("page", 1)
                                if st.button(f"REF_{i+1} · p.{p}", key=f"btn_ref_{msg_idx}_{i}", type=btn_kind, use_container_width=True):
                                    st.session_state.active_ref = i + 1
                                    st.session_state.active_citation = cite
                                    st.session_state.current_page = p
                                    st.rerun()

                    # Message footer line
                    st.markdown(f'<div style="padding-left: 42px;">{footer_html}</div><div style="height: 14px;"></div>', unsafe_allow_html=True)

            # If currently querying, execute API call live inside the container
            if st.session_state.is_querying and active_query:
                doc_to_query = st.session_state.selected_doc_id
                if not doc_to_query and docs:
                    doc_to_query = docs[0]["doc_id"]
                    st.session_state.selected_doc_id = doc_to_query

                if not doc_to_query:
                    st.markdown('<div class="inline-error">Please upload or select an indexed document first.</div>', unsafe_allow_html=True)
                else:
                    thinking_ph = st.empty()
                    thinking_ph.markdown("""
                    <div class="thinking-line" style="padding-left: 10px;">
                        <span class="thinking-dot"></span>
                        <span>Analyzing document layout and retrieving grounded evidence...</span>
                    </div>
                    """, unsafe_allow_html=True)

                    t0 = time.time()
                    payload = {
                        "query": active_query,
                        "doc_id": doc_to_query
                    }
                    try:
                        res = requests.post(f"{BACKEND_URL}/query", json=payload, timeout=90)
                        latency = time.time() - t0
                        thinking_ph.empty()
                        if res.status_code == 200:
                            data = res.json()
                            assistant_msg = {
                                "role": "assistant",
                                "content": data.get("answer", ""),
                                "route": data.get("route_taken", "direct_text"),
                                "citations": data.get("citations", []),
                                "calc_code": data.get("calculation_code"),
                                "calc_result": data.get("calculation_result"),
                                "verification_passed": data.get("verification_passed", True),
                                "verification_notes": data.get("verification_notes"),
                                "reasoning_steps": data.get("reasoning_steps", []),
                                "latency": latency
                            }
                            st.session_state.messages.append(assistant_msg)
                            cites = data.get("citations", [])
                            if cites:
                                st.session_state.active_ref = 1
                                st.session_state.active_citation = cites[0]
                                st.session_state.current_page = cites[0].get("page", 1)
                            st.session_state.is_querying = False
                            st.rerun()
                        else:
                            st.markdown(f'<div class="inline-error">Server query error: {html.escape(res.text)}</div>', unsafe_allow_html=True)
                    except Exception as ex:
                        thinking_ph.empty()
                        st.markdown(f'<div class="inline-error">Query failed: {html.escape(str(ex))}</div>', unsafe_allow_html=True)

        # Suggestion Chips below conversation
        st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            if st.button("List the technical skills", key="sug_skills", use_container_width=True, type="secondary"):
                st.session_state.pending_query = "What are the key technical skills and findings surveyed in this paper?"
                st.rerun()
        with col_s2:
            if st.button("Where did she work?", key="sug_work", use_container_width=True, type="secondary"):
                st.session_state.pending_query = "Where did the author work or what institutions are affiliated?"
                st.rerun()
        with col_s3:
            if st.button("Sum numeric table columns", key="sug_sum", use_container_width=True, type="secondary"):
                st.session_state.pending_query = "Calculate the total revenue from Q1 to Q4 from the table"
                st.rerun()

        # Chat Input
        user_input = st.chat_input("Ask a question about the document...")
        if user_input:
            st.session_state.pending_query = user_input
            st.rerun()


# ==========================================
# 4. VISUAL GROUNDING (RIGHT CARD)
# ==========================================
def render_viewer(docs: List[Dict[str, Any]]):
    with st.container(border=True):
        doc_id = st.session_state.selected_doc_id
        selected_meta = next((d for d in docs if d["doc_id"] == doc_id), None) if doc_id else None
        total_pages = selected_meta.get("num_pages", 1) if selected_meta else 1

        # Card Header with Prev / Page X of N / Next
        col_t, col_n1, col_pg, col_n2 = st.columns([1.8, 0.7, 1.2, 0.7])
        with col_t:
            st.markdown('<div class="card-title" style="margin-top: 5px;">Visual grounding</div>', unsafe_allow_html=True)
        with col_n1:
            prev_disabled = (st.session_state.current_page <= 1) or (not doc_id)
            if st.button("Prev", key="btn_prev_page", disabled=prev_disabled, use_container_width=True, type="secondary"):
                if st.session_state.current_page > 1:
                    st.session_state.current_page -= 1
                    if st.session_state.active_citation and st.session_state.active_citation.get("page") != st.session_state.current_page:
                        st.session_state.active_ref = None
                        st.session_state.active_citation = None
                    st.rerun()
        with col_pg:
            pg_text = f"Page {st.session_state.current_page} of {total_pages}" if doc_id else "Page 1 of 1"
            st.markdown(f'<div style="text-align: center; font-size: 12px; color: var(--mut); margin-top: 8px; font-weight: 500;">{pg_text}</div>', unsafe_allow_html=True)
        with col_n2:
            next_disabled = (st.session_state.current_page >= total_pages) or (not doc_id)
            if st.button("Next", key="btn_next_page", disabled=next_disabled, use_container_width=True, type="secondary"):
                if st.session_state.current_page < total_pages:
                    st.session_state.current_page += 1
                    if st.session_state.active_citation and st.session_state.active_citation.get("page") != st.session_state.current_page:
                        st.session_state.active_ref = None
                        st.session_state.active_citation = None
                    st.rerun()

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        if not doc_id:
            # Empty state: centered muted card with upload icon
            st.markdown("""
            <div class="empty-card" style="padding: 120px 20px;">
                <div class="empty-card-icon">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="17 8 12 3 7 8"></polyline>
                        <line x1="12" y1="3" x2="12" y2="15"></line>
                    </svg>
                </div>
                <div class="empty-card-text">Upload a PDF to begin</div>
            </div>
            """, unsafe_allow_html=True)
            return

        # Fetch page image from backend vision renderer
        p_url = f"{BACKEND_URL}/documents/{doc_id}/pages/{st.session_state.current_page}"
        try:
            p_res = requests.get(p_url, timeout=12)
            if p_res.status_code == 200:
                raw_bytes = p_res.content

                # Check if active citation matches current page
                active_cite = st.session_state.active_citation
                if active_cite and active_cite.get("page") == st.session_state.current_page:
                    render_bytes = draw_sand_highlight(raw_bytes, active_cite.get("bbox", {}))
                else:
                    render_bytes = raw_bytes

                b64_img = base64.b64encode(render_bytes).decode("utf-8")
                st.markdown(f"""
                <div class="page-frame">
                    <img src="data:image/png;base64,{b64_img}" alt="Document Page {st.session_state.current_page}" />
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="inline-error">Could not load page image (Status {p_res.status_code}).</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="inline-error">Error fetching page image: {html.escape(str(e))}</div>', unsafe_allow_html=True)

        # Evidence Strip Under the Page
        active_cite = st.session_state.active_citation
        if active_cite:
            ref_idx = st.session_state.get("active_ref", 1)
            p_num = active_cite.get("page", st.session_state.current_page)
            bbox = active_cite.get("bbox", {})
            x0 = int(bbox.get("x0", 0))
            y0 = int(bbox.get("y0", 0))
            x1 = int(bbox.get("x1", 0))
            y1 = int(bbox.get("y1", 0))
            passage = active_cite.get("quoted_snippet", "Evidence region highlighted on page.")

            st.markdown(f"""
            <div class="evidence-strip">
                <div class="evidence-header">
                    <span>Evidence · REF_{ref_idx}</span>
                    <span class="evidence-meta">page {p_num} · bbox ({x0}, {y0}, {x1}, {y1})</span>
                </div>
                <div class="evidence-passage">"{html.escape(passage)}"</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="evidence-strip">
                <div class="evidence-header">
                    <span>Evidence · Visual Grounding</span>
                    <span class="evidence-meta">page {st.session_state.current_page}</span>
                </div>
                <div class="evidence-passage">Click any citation reference [REF_n] in the conversation to inspect grounded coordinates and passage.</div>
            </div>
            """, unsafe_allow_html=True)


# ==========================================
# 5. MAIN ENTRY POINT
# ==========================================
def main():
    docs = fetch_documents()
    # Ensure active document is always initialized if documents exist
    if docs and not st.session_state.selected_doc_id:
        st.session_state.selected_doc_id = docs[0]["doc_id"]

    render_sidebar(docs)
    render_header()

    col_chat, col_viewer = st.columns([1.15, 1.0], gap="medium")
    with col_chat:
        render_chat(docs)
    with col_viewer:
        render_viewer(docs)


if __name__ == "__main__":
    main()
