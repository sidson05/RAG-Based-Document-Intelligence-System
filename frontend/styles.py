"""
Executive Light Theme Design Tokens & CSS Styles
DocIntel - RAG-Based Document Intelligent System
"""

def load_css() -> str:
    return """
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600&family=Playfair+Display:ital,wght@0,500;0,600;1,500;1,600&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --bg: #f7f5f0;
        --panel: #ffffff;
        --panel2: #f6f4ee;
        --line: #e8e4db;
        --tx: #1d2a24;
        --mut: #6b776f;
        --acc: #2d4a3e;
        --acc-soft: #e8efe4;
        --sage: #5f8a45;
        --forest: #1f3a30;
        --cream: #eaf0e6;
        --sand: #d9a441;
        --good: #4f8a55;
        --warn: #b98a3a;
        --clay: #b5604f;
        --clay-bg: rgba(181, 96, 79, 0.13);
    }

    /* Global Typography & Base Settings */
    *, *::before, *::after {
        box-sizing: border-box;
    }

    html, body, [data-testid="stAppViewContainer"], .stApp {
        font-family: 'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        font-variant-numeric: lining-nums !important;
        color: var(--tx) !important;
        background-color: var(--bg) !important;
        font-size: 14px;
        font-weight: 400;
    }

    p, label, button, input, textarea, select {
        font-family: 'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-variant-numeric: lining-nums;
    }

    span:not([class*="material"]):not([data-testid*="Icon"]):not([data-testid*="icon"]):not([class*="StyledIcon"]):not([data-testid="stExpanderToggleIcon"]),
    div:not([class*="material"]):not([data-testid*="Icon"]):not([data-testid*="icon"]):not([class*="StyledIcon"]):not([data-testid="stExpanderToggleIcon"]) {
        font-family: 'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-variant-numeric: lining-nums;
    }

    /* Never override icon fonts / ligatures */
    [data-testid*="Icon"], [data-testid*="icon"], [class*="Icon"], [class*="icon"],
    [class*="material-symbols"], [class*="StyledIcon"], [data-testid="stExpanderToggleIcon"] {
        font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
        letter-spacing: normal !important;
        white-space: nowrap !important;
    }

    /* Hide Streamlit Header, Footer, and Main Menu */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    #MainMenu, footer {
        visibility: hidden !important;
        display: none !important;
    }

    /* Top padding adjustment */
    .stMainBlockContainer, [data-testid="stMainBlockContainer"] {
        padding-top: 1.8rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1440px !important;
        margin: 0 auto !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: var(--panel) !important;
        border-right: 1px solid var(--line) !important;
    }
    [data-testid="stSidebarContent"] {
        background-color: var(--panel) !important;
        padding: 22px 20px !important;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.85rem !important;
    }

    /* Brand Block */
    .brand-block {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
    }
    .brand-tile {
        width: 34px;
        height: 34px;
        border-radius: 10px;
        background-color: var(--forest);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--cream);
        flex-shrink: 0;
    }
    .brand-name {
        font-size: 16px;
        font-weight: 600;
        color: var(--forest);
        line-height: 1.2;
        letter-spacing: -0.01em;
    }
    .brand-sub {
        font-size: 11.5px;
        color: var(--mut);
        line-height: 1.2;
    }

    /* Section Labels */
    .section-label {
        font-size: 10.5px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--mut);
        margin-top: 14px;
        margin-bottom: 4px;
    }
    .helper-text {
        font-size: 12.5px;
        color: var(--mut);
        line-height: 1.4;
        margin-bottom: 12px;
    }

    /* File Uploader Dropzone */
    [data-testid="stFileUploader"] {
        margin-bottom: 8px !important;
    }
    [data-testid="stFileUploader"] section {
        border: 1.5px dashed #cfc9bb !important;
        background-color: var(--panel2) !important;
        border-radius: 14px !important;
        padding: 18px 14px !important;
        transition: all 0.2s ease-in-out !important;
        color: var(--mut) !important;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: var(--acc) !important;
        background-color: var(--acc-soft) !important;
    }
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] {
        color: var(--mut) !important;
        font-size: 12px !important;
    }

    /* Compact Uploaded File Chip */
    .file-chip {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 12px;
        background-color: var(--panel2);
        border: 1px solid var(--line);
        border-radius: 10px;
        margin-top: 6px;
        margin-bottom: 10px;
    }
    .file-chip-icon {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        background-color: var(--acc-soft);
        color: var(--acc);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .file-chip-info {
        overflow: hidden;
        flex: 1;
    }
    .file-chip-name {
        font-size: 13px;
        font-weight: 600;
        color: var(--tx);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 190px;
    }
    .file-chip-size {
        font-size: 11px;
        color: var(--mut);
    }

    /* Buttons Styling */
    .stButton > button {
        border-radius: 99px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        transition: all 0.15s ease-in-out !important;
        padding: 7px 18px !important;
        box-shadow: none !important;
    }
    .stButton > button:focus {
        outline: 2px solid var(--acc) !important;
        outline-offset: 1px !important;
    }
    /* Primary Pill Button */
    .stButton > button[kind="primary"], .stButton > button:has(.primary-flag) {
        background-color: var(--forest) !important;
        color: var(--cream) !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: var(--acc) !important;
        color: var(--cream) !important;
    }
    /* Secondary Pill Button */
    .stButton > button[kind="secondary"] {
        background-color: var(--panel) !important;
        color: var(--tx) !important;
        border: 1px solid var(--line) !important;
    }
    .stButton > button[kind="secondary"]:hover:not(:disabled) {
        background-color: var(--acc-soft) !important;
        border-color: var(--acc) !important;
        color: var(--acc) !important;
    }
    .stButton > button:disabled {
        background-color: var(--panel2) !important;
        color: #a4aca6 !important;
        border-color: var(--line) !important;
        cursor: not-allowed !important;
    }

    /* Processing Checklist */
    .checklist-box {
        background-color: var(--panel2);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 12px 14px;
        margin: 10px 0;
    }
    .checklist-item {
        display: flex;
        align-items: center;
        gap: 9px;
        font-size: 12.5px;
        margin: 6px 0;
        color: var(--tx);
    }
    .check-circle {
        width: 17px;
        height: 17px;
        border-radius: 50%;
        background-color: var(--good);
        color: #ffffff;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 10.5px;
        font-weight: 600;
        flex-shrink: 0;
    }
    .check-pending {
        width: 17px;
        height: 17px;
        border-radius: 50%;
        border: 1.5px solid #d3cdc3;
        background-color: var(--panel2);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    /* Selectbox Pill */
    [data-baseweb="select"] {
        border-radius: 99px !important;
    }
    [data-baseweb="select"] > div {
        border-radius: 99px !important;
        background-color: var(--panel2) !important;
        border: 1px solid var(--line) !important;
        font-size: 13px !important;
        color: var(--tx) !important;
        padding: 2px 8px !important;
    }
    [data-baseweb="select"] > div:hover {
        border-color: #cfc9bb !important;
    }
    [data-baseweb="select"] > div:focus-within {
        border-color: var(--acc) !important;
        outline: 2px solid var(--acc) !important;
        outline-offset: 1px !important;
    }

    /* Expander */
    [data-testid="stExpander"] {
        background-color: var(--panel2) !important;
        border: 1px solid var(--line) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        margin-top: 10px !important;
    }
    [data-testid="stExpander"] details {
        border: none !important;
        background-color: transparent !important;
    }
    [data-testid="stExpander"] summary {
        color: var(--tx) !important;
        font-size: 12.5px !important;
        font-weight: 600 !important;
        cursor: pointer !important;
    }
    [data-testid="stExpander"] summary:hover {
        color: var(--acc) !important;
    }
    [data-testid="stExpander"] summary p {
        font-size: 12.5px !important;
        font-weight: 600 !important;
        color: var(--tx) !important;
        margin: 0 !important;
        padding-left: 4px !important;
    }
    [data-testid="stExpanderToggleIcon"] {
        color: var(--mut) !important;
        flex-shrink: 0 !important;
    }
    .metrics-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6px 14px;
        font-size: 12px;
        padding: 4px 2px;
    }
    .metric-k {
        color: var(--mut);
        font-weight: 400;
    }
    .metric-v {
        color: var(--tx);
        font-weight: 600;
        text-align: right;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Main Area Header */
    .paper-badge {
        background-color: var(--acc-soft);
        color: var(--acc);
        padding: 4px 14px;
        border-radius: 99px;
        font-weight: 600;
        font-size: 12px;
        display: inline-block;
        margin-bottom: 8px;
        border: 1px solid rgba(45, 74, 62, 0.15);
    }
    .page-title {
        font-family: 'Playfair Display', Georgia, serif !important;
        font-weight: 600 !important;
        font-size: 32px !important;
        line-height: 1.25 !important;
        color: var(--forest) !important;
        margin-top: 4px !important;
        margin-bottom: 6px !important;
        letter-spacing: -0.015em !important;
    }
    .page-subtitle {
        font-size: 13.5px;
        color: var(--mut);
        line-height: 1.45;
        margin-bottom: 16px;
    }
    .pipeline-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 22px;
    }
    .pipeline-pill {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background-color: var(--panel);
        border: 1px solid var(--line);
        border-radius: 99px;
        padding: 5px 13px;
        font-size: 12px;
        color: var(--tx);
        font-weight: 500;
    }
    .sage-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: var(--sage);
        display: inline-block;
        flex-shrink: 0;
    }

    /* Card Panels */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: var(--panel) !important;
        border: 1px solid var(--line) !important;
        border-radius: 18px !important;
        padding: 16px 18px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
    }
    .card-header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 14px;
        padding-bottom: 10px;
        border-bottom: 1px solid var(--line);
    }
    .card-title {
        font-size: 15px;
        font-weight: 600;
        color: var(--forest);
        letter-spacing: -0.01em;
    }
    .card-model-tag {
        font-size: 11.5px;
        color: var(--mut);
        background-color: var(--panel2);
        padding: 3px 9px;
        border-radius: 6px;
        border: 1px solid var(--line);
        font-family: 'JetBrains Mono', monospace;
    }

    /* Chat Messages */
    .chat-bubble-user {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 14px;
    }
    .user-pill {
        background-color: var(--forest);
        color: var(--cream);
        border-radius: 16px 16px 4px 16px;
        padding: 10px 16px;
        font-size: 13.5px;
        line-height: 1.5;
        max-width: 82%;
        word-wrap: break-word;
    }
    .chat-row-assistant {
        display: flex;
        gap: 12px;
        margin-bottom: 20px;
        align-items: flex-start;
    }
    .assistant-avatar {
        width: 30px;
        height: 30px;
        border-radius: 10px;
        background-color: var(--acc-soft);
        color: var(--acc);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 600;
        flex-shrink: 0;
        margin-top: 2px;
    }
    .assistant-body {
        flex: 1;
        overflow-x: hidden;
    }
    .tags-row {
        display: flex;
        gap: 7px;
        margin-bottom: 8px;
        flex-wrap: wrap;
        align-items: center;
    }
    .tag-route {
        background-color: var(--panel2);
        border: 1px solid var(--line);
        color: var(--mut);
        font-size: 11.5px;
        font-weight: 600;
        padding: 2.5px 10px;
        border-radius: 99px;
        display: inline-block;
        letter-spacing: 0.02em;
    }
    .tag-verified {
        background-color: #e4f0e3;
        color: var(--good);
        font-size: 11.5px;
        font-weight: 600;
        padding: 2.5px 10px;
        border-radius: 99px;
        display: inline-block;
        border: 1px solid rgba(79, 138, 85, 0.2);
    }
    .tag-unverified {
        background-color: #f6ecd6;
        color: var(--warn);
        font-size: 11.5px;
        font-weight: 600;
        padding: 2.5px 10px;
        border-radius: 99px;
        display: inline-block;
        border: 1px solid rgba(185, 138, 58, 0.2);
    }
    .answer-text {
        font-size: 14px;
        line-height: 1.6;
        color: var(--tx);
    }
    .answer-text ul, .answer-text ol {
        padding-left: 18px !important;
        margin-top: 6px;
        margin-bottom: 6px;
    }
    .answer-text li {
        margin-bottom: 4px;
    }

    /* Clickable REF Chips */
    .ref-chip {
        display: inline-block;
        padding: 2px 7px;
        border-radius: 6px;
        background-color: var(--acc-soft);
        color: var(--acc);
        font-size: 11px;
        font-weight: 600;
        margin: 0 2px;
        cursor: pointer;
        text-decoration: none;
        border: 1px solid rgba(45, 74, 62, 0.18);
        transition: all 0.15s ease;
    }
    .ref-chip:hover {
        background-color: var(--acc);
        color: var(--cream);
    }
    .ref-chip.active {
        background-color: var(--forest) !important;
        color: var(--cream) !important;
        border-color: var(--forest) !important;
    }

    /* Code Block in Assistant */
    .code-block-box {
        background-color: var(--panel2);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 10px 14px;
        margin: 10px 0;
        overflow-x: auto;
    }
    .code-block-header {
        font-size: 11px;
        font-weight: 600;
        color: var(--mut);
        margin-bottom: 6px;
        letter-spacing: 0.04em;
    }
    .code-block-code {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
        color: var(--tx);
        line-height: 1.45;
        white-space: pre-wrap;
        margin: 0;
    }
    .code-block-result {
        margin-top: 8px;
        padding-top: 6px;
        border-top: 1px dashed var(--line);
        font-size: 11.5px;
        color: var(--forest);
        font-weight: 500;
    }

    /* Message Footer */
    .msg-footer {
        font-size: 11.5px;
        color: var(--mut);
        margin-top: 8px;
    }

    /* Chat Input */
    [data-testid="stChatInput"] {
        background-color: transparent !important;
        padding: 0 !important;
    }
    [data-testid="stChatInput"] > div {
        background-color: var(--panel2) !important;
        border: 1px solid var(--line) !important;
        border-radius: 99px !important;
        padding: 4px 14px !important;
        transition: border-color 0.15s ease;
    }
    [data-testid="stChatInput"] > div:focus-within {
        border-color: var(--acc) !important;
        box-shadow: 0 0 0 1px var(--acc) !important;
    }
    [data-testid="stChatInput"] textarea {
        color: var(--tx) !important;
        font-size: 13.5px !important;
    }

    /* Visual Grounding Page Viewer */
    .page-frame {
        background-color: var(--panel);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: hidden;
        margin-bottom: 12px;
    }
    .page-frame img {
        border-radius: 6px;
        max-width: 100%;
        height: auto;
        display: block;
    }

    /* Evidence Strip */
    .evidence-strip {
        background-color: var(--panel2);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 12px 14px;
        font-size: 12.5px;
        margin-top: 10px;
    }
    .evidence-header {
        font-weight: 600;
        color: var(--forest);
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4px;
    }
    .evidence-meta {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: var(--mut);
        font-weight: 400;
    }
    .evidence-passage {
        color: var(--mut);
        line-height: 1.45;
        margin-top: 4px;
        font-style: italic;
    }

    /* Empty, Loading, and Error States */
    .empty-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 55px 20px;
        text-align: center;
        color: var(--mut);
        background-color: var(--panel2);
        border: 1.5px dashed var(--line);
        border-radius: 14px;
    }
    .empty-card-icon {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        background-color: var(--panel);
        border: 1px solid var(--line);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 12px;
        color: var(--acc);
    }
    .empty-card-text {
        font-size: 13.5px;
        font-weight: 500;
        color: var(--mut);
    }
    .thinking-line {
        display: flex;
        align-items: center;
        gap: 9px;
        font-size: 13px;
        color: var(--mut);
        padding: 10px 0;
    }
    @keyframes pulse-dot {
        0%, 100% { opacity: 0.35; transform: scale(0.9); }
        50% { opacity: 1; transform: scale(1.2); }
    }
    .thinking-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: var(--sage);
        display: inline-block;
        animation: pulse-dot 1.2s infinite ease-in-out;
        flex-shrink: 0;
    }
    .inline-error {
        background-color: var(--clay-bg);
        color: var(--clay);
        border: 1px solid rgba(181, 96, 79, 0.28);
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 13px;
        margin: 10px 0;
        line-height: 1.45;
    }

    /* Responsiveness */
    @media (max-width: 1100px) {
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
        }
    }
    """

