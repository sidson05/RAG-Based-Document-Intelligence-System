import streamlit as st
import requests
import json
from pathlib import Path
from PIL import Image
import io

# Page Configuration
st.set_page_config(
    page_title="RAG-Based Document Intelligent System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_URL = "http://127.0.0.1:8000/api"

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .paper-badge {
        background-color: #EEF2FF;
        color: #4F46E5;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
        margin-bottom: 1rem;
        border: 1px solid #C7D2FE;
    }
    .route-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 5px;
    }
    .badge-calc { background-color: #FEF3C7; color: #D97706; border: 1px solid #FDE68A; }
    .badge-text { background-color: #E0E7FF; color: #4338CA; border: 1px solid #C7D2FE; }
    .badge-visual { background-color: #FCE7F3; color: #DB2777; border: 1px solid #FBCFE8; }
    .badge-faithful { background-color: #D1FAE5; color: #059669; border: 1px solid #A7F3D0; }
    .citation-box {
        background-color: #F8FAFC;
        border-left: 3px solid #3B82F6;
        padding: 8px 12px;
        margin: 6px 0;
        border-radius: 0 6px 6px 0;
        font-size: 0.88rem;
    }
</style>
""", unsafe_allow_html=True)

# State Management
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_doc_id" not in st.session_state:
    st.session_state.selected_doc_id = None
if "current_page" not in st.session_state:
    st.session_state.current_page = 1
if "highlighted_img_bytes" not in st.session_state:
    st.session_state.highlighted_img_bytes = None

def fetch_documents():
    try:
        r = requests.get(f"{BACKEND_URL}/documents", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return []
    return []

# Sidebar
with st.sidebar:
    st.markdown("### 📁 Document Ingestion")
    st.caption("Supports layout-aware parsing, table structure recognition (TSR), and visual rendering.")
    
    uploaded_file = st.file_uploader("Upload PDF Document", type=["pdf"])
    if uploaded_file is not None:
        if st.button("🚀 Process & Index Document", use_container_width=True):
            with st.spinner("Parsing layout, extracting tables & indexing embeddings..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                try:
                    res = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=60)
                    if res.status_code == 200:
                        meta = res.json()
                        st.success(f"Indexed: {meta['filename']}")
                        st.session_state.selected_doc_id = meta["doc_id"]
                        st.rerun()
                    else:
                        st.error(f"Upload failed: {res.text}")
                except Exception as e:
                    st.error(f"Server connection error: {e}")

    docs = fetch_documents()
    if docs:
        st.markdown("---")
        st.markdown("### 📚 Indexed Documents")
        doc_options = {d["doc_id"]: f"{d['filename']} ({d['num_pages']} pgs, {d['num_tables']} tbls)" for d in docs}
        selected_id = st.selectbox(
            "Select Active Document",
            options=list(doc_options.keys()),
            format_func=lambda x: doc_options[x],
            index=0 if not st.session_state.selected_doc_id else list(doc_options.keys()).index(st.session_state.selected_doc_id) if st.session_state.selected_doc_id in doc_options else 0
        )
        st.session_state.selected_doc_id = selected_id
        
        # Display selected document metadata
        selected_meta = next(d for d in docs if d["doc_id"] == selected_id)
        with st.expander("Document Metadata & Metrics", expanded=False):
            st.write(f"**Pages:** {selected_meta['num_pages']}")
            st.write(f"**Layout Blocks:** {selected_meta['num_blocks']}")
            st.write(f"**Tables Detected:** {selected_meta['num_tables']}")
            st.write(f"**Indexed Chunks:** {selected_meta['num_chunks']}")
    else:
        st.info("No documents uploaded yet. Upload a PDF to begin.")

    st.markdown("---")
    st.markdown("### ⚙️ System Architecture")
    st.caption("**Research Foundation:** ACM TOIS 2026 (Ke et al.)")
    st.markdown("""
    - **Parsing:** PyMuPDF + pdfplumber DLA
    - **Indexing:** FAISS Dense + BM25 Sparse
    - **Retrieval:** Reciprocal Rank Fusion (RRF)
    - **Reranker:** Cross-Encoder
    - **Agent Tools:** Code Interpreter + VLM
    - **Auditor:** Self-Reflection Verifier
    """)

# Main Screen Header
st.markdown('<div class="paper-badge">ACM TOIS 2026 • Survey-Aligned Architecture • DOI: 10.1145/3768156</div>', unsafe_allow_html=True)
st.markdown('<div class="main-header">RAG-Based Document Intelligent System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Unified Hybrid RAG Architecture: Layout-Aware Parsing, Tabular Code Interpreter, Visual Grounding & Hallucination Auditor</div>', unsafe_allow_html=True)

# Split view: Chat (Left 55%) vs Visual Document Grounding (Right 45%)
col_chat, col_viewer = st.columns([1.2, 1.0], gap="large")

with col_chat:
    st.markdown("#### 💬 Intelligent Assistant")
    
    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                # Route and Verification Badges
                route = msg.get("route", "direct_text")
                badge_class = "badge-calc" if "calc" in route else "badge-visual" if "visual" in route else "badge-text"
                st.markdown(
                    f'<span class="route-badge {badge_class}">Route: {route.upper()}</span> '
                    f'<span class="route-badge badge-faithful">✓ Verified Faithful</span>',
                    unsafe_allow_html=True
                )
                
                # Answer content
                st.markdown(msg["content"])
                
                # Code execution if any
                if msg.get("calc_code"):
                    with st.expander("💻 Deterministic Python/Pandas Code Executed", expanded=False):
                        st.code(msg["calc_code"], language="python")
                        st.caption(f"Execution Output: {msg.get('calc_result')}")
                        
                # Citations
                citations = msg.get("citations", [])
                if citations:
                    st.markdown("**📌 Grounded Sources & Citations:**")
                    for i, c in enumerate(citations):
                        bbox = c.get("bbox", {})
                        p = c.get("page", 1)
                        btn_label = f"🔍 View Page {p} Evidence"
                        if st.button(btn_label, key=f"cite_{msg.get('id', '')}_{i}"):
                            # Trigger highlight on viewer
                            if st.session_state.selected_doc_id:
                                try:
                                    h_res = requests.post(
                                        f"{BACKEND_URL}/documents/{st.session_state.selected_doc_id}/highlight",
                                        json={"bbox": bbox},
                                        timeout=10
                                    )
                                    if h_res.status_code == 200:
                                        st.session_state.highlighted_img_bytes = h_res.content
                                        st.session_state.current_page = p
                                        st.rerun()
                                except Exception as err:
                                    st.error(f"Highlight error: {err}")
                        st.markdown(f'<div class="citation-box"><b>Page {p}:</b> {c.get("quoted_snippet", "")}</div>', unsafe_allow_html=True)
                        
                # Agent reasoning steps
                if msg.get("reasoning_steps"):
                    with st.expander("🧠 Agentic Pipeline Reasoning Trace", expanded=False):
                        for step in msg["reasoning_steps"]:
                            st.write(f"- {step}")
            else:
                st.markdown(msg["content"])

    # User query input
    user_query = st.chat_input("Ask a question about the document, tabular data, or visual elements...")
    if user_query:
        # Append user message
        st.session_state.messages.append({"role": "user", "content": user_query})
        
        with st.chat_message("user"):
            st.markdown(user_query)
            
        with st.chat_message("assistant"):
            with st.spinner("Analyzing document layout, executing hybrid retrieval & agentic reasoning..."):
                payload = {
                    "query": user_query,
                    "doc_id": st.session_state.selected_doc_id
                }
                try:
                    res = requests.post(f"{BACKEND_URL}/query", json=payload, timeout=60)
                    if res.status_code == 200:
                        data = res.json()
                        import uuid
                        msg_id = uuid.uuid4().hex[:6]
                        
                        # Store assistant message
                        assistant_msg = {
                            "id": msg_id,
                            "role": "assistant",
                            "content": data["answer"],
                            "route": data["route_taken"],
                            "citations": data["citations"],
                            "calc_code": data["calculation_code"],
                            "calc_result": data["calculation_result"],
                            "verification_passed": data["verification_passed"],
                            "verification_notes": data["verification_notes"],
                            "reasoning_steps": data["reasoning_steps"]
                        }
                        st.session_state.messages.append(assistant_msg)
                        
                        # Set highlighted image if citations exist
                        if data["citations"] and st.session_state.selected_doc_id:
                            first_cite = data["citations"][0]
                            st.session_state.current_page = first_cite["page"]
                            try:
                                h_res = requests.post(
                                    f"{BACKEND_URL}/documents/{st.session_state.selected_doc_id}/highlight",
                                    json={"bbox": first_cite["bbox"]},
                                    timeout=10
                                )
                                if h_res.status_code == 200:
                                    st.session_state.highlighted_img_bytes = h_res.content
                            except Exception:
                                pass
                                
                        st.rerun()
                    else:
                        st.error(f"Error from server: {res.text}")
                except Exception as e:
                    st.error(f"Request failed: {e}")

with col_viewer:
    st.markdown("#### 👁️ Visual Grounding & Document Viewer")
    
    if st.session_state.selected_doc_id:
        doc_id = st.session_state.selected_doc_id
        
        # Navigation bar
        c_nav1, c_nav2, c_nav3 = st.columns([1, 2, 1])
        with c_nav1:
            if st.button("◀ Prev"):
                if st.session_state.current_page > 1:
                    st.session_state.current_page -= 1
                    st.session_state.highlighted_img_bytes = None
                    st.rerun()
        with c_nav2:
            st.markdown(f"<p style='text-align: center; margin-top: 5px;'><b>Page {st.session_state.current_page}</b></p>", unsafe_allow_html=True)
        with c_nav3:
            if st.button("Next ▶"):
                st.session_state.current_page += 1
                st.session_state.highlighted_img_bytes = None
                st.rerun()
                
        # Image display
        if st.session_state.highlighted_img_bytes:
            st.image(
                st.session_state.highlighted_img_bytes,
                caption=f"Visual Citation Grounding on Page {st.session_state.current_page}",
                use_container_width=True
            )
            if st.button("Clear Citation Highlight"):
                st.session_state.highlighted_img_bytes = None
                st.rerun()
        else:
            try:
                p_url = f"{BACKEND_URL}/documents/{doc_id}/pages/{st.session_state.current_page}"
                p_res = requests.get(p_url, timeout=10)
                if p_res.status_code == 200:
                    st.image(p_res.content, caption=f"Document Page {st.session_state.current_page}", use_container_width=True)
                else:
                    st.warning("Could not load page image.")
            except Exception as e:
                st.error(f"Failed to fetch page image: {e}")
    else:
        st.info("Upload and select a document to inspect pages and visual bounding box citations.")
