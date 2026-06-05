import html
import streamlit as st


# ==================================================
# Clean0ps UI System
# Shared styling, navigation, cards, badges, steppers,
# empty states, callouts, and reusable layout helpers.
# ==================================================


# --------------------------------------------------
# Navigation
# --------------------------------------------------

def render_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-logo">C</div>
                <div>
                    <div class="sidebar-title">Clean0ps</div>
                    <div class="sidebar-subtitle">Data Cleaning Toolkit</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="sidebar-section-label">MAIN</div>',
            unsafe_allow_html=True
        )

        st.page_link(
            "app.py",
            label="Home"
        )

        st.markdown(
            '<div class="sidebar-section-label">CLEANING</div>',
            unsafe_allow_html=True
        )

        st.page_link(
            "pages/4_Template Cleaning Engine.py",
            label="Template Cleaning Engine"
        )

        st.page_link(
            "pages/2_Data_Quality_Dashboard.py",
            label="Data Quality + Validation"
        )

        st.page_link(
            "pages/6_Document_Standards_Cleanup_Lab.py",
            label="Document Standards Cleanup"
        )

        st.markdown(
            '<div class="sidebar-section-label">ANALYTICS</div>',
            unsafe_allow_html=True
        )

        st.page_link(
            "pages/5_Ecommerce_Analytics_Lab.py",
            label="E-commerce Analytics Lab"
        )

        st.page_link(
            "pages/1_Inventory_Dashboard.py",
            label="Inventory Dashboard"
        )

        st.markdown(
            '<div class="sidebar-section-label">WORKFLOWS</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="sidebar-workflow-card">
                <div class="sidebar-workflow-title">Best For</div>
                <div class="sidebar-workflow-text">
                    CSV cleanup, Excel cleanup, CRM lists, inventory files,
                    document standards cleanup, e-commerce reporting,
                    data audits, validation checks, and client-ready exports.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="sidebar-status">
                <div class="sidebar-status-dot"></div>
                <div>
                    <div class="sidebar-status-title">Local Build</div>
                    <div class="sidebar-status-text">Running in development</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_top_nav():
    st.markdown(
        """
        <div class="top-nav-wrapper">
            <div class="top-nav-title">Clean0ps Navigation</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    nav_cols = st.columns(6)

    with nav_cols[0]:
        st.page_link(
            "app.py",
            label="Home"
        )

    with nav_cols[1]:
        st.page_link(
            "pages/4_Template Cleaning Engine.py",
            label="Clean"
        )

    with nav_cols[2]:
        st.page_link(
            "pages/2_Data_Quality_Dashboard.py",
            label="Quality"
        )

    with nav_cols[3]:
        st.page_link(
            "pages/6_Document_Standards_Cleanup_Lab.py",
            label="Docs"
        )

    with nav_cols[4]:
        st.page_link(
            "pages/1_Inventory_Dashboard.py",
            label="Inventory"
        )

    with nav_cols[5]:
        st.page_link(
            "pages/5_Ecommerce_Analytics_Lab.py",
            label="E-commerce"
        )



def apply_clean0ps_style():
    st.markdown(
        """
        <style>
        :root {
            --clean0ps-bg: #0B1120;
            --clean0ps-bg-dark: #020617;
            --clean0ps-panel: #111827;
            --clean0ps-panel-soft: #0F172A;
            --clean0ps-card: #111827;
            --clean0ps-card-light: #1E293B;
            --clean0ps-border: #334155;
            --clean0ps-border-soft: rgba(148, 163, 184, 0.28);
            --clean0ps-text: #E5E7EB;
            --clean0ps-text-strong: #F8FAFC;
            --clean0ps-muted: #94A3B8;
            --clean0ps-blue: #38BDF8;
            --clean0ps-blue-dark: #0EA5E9;
            --clean0ps-green: #22C55E;
            --clean0ps-red: #F87171;
            --clean0ps-yellow: #FACC15;
            --clean0ps-purple: #A78BFA;
        }

        html,
        body,
        #root,
        .stApp,
        [data-testid="stApp"],
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewContainer"] > .main {
            background:
                radial-gradient(circle at top left, #111827 0%, #0B1120 44%, #020617 100%) !important;
            color: var(--clean0ps-text) !important;
        }

        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="stHeaderActionElements"],
        .stDeployButton,
        header {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }

        .block-container {
            padding-top: 1.25rem !important;
            padding-bottom: 3rem !important;
            max-width: 1180px !important;
        }

        /* Top navigation */
        .top-nav-wrapper {
            padding: 0.85rem 1rem;
            border-radius: 18px;
            background: linear-gradient(
                135deg,
                rgba(15, 23, 42, 0.96) 0%,
                rgba(30, 41, 59, 0.86) 100%
            );
            border: 1px solid rgba(51, 65, 85, 0.95);
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.20);
            margin-bottom: 0.6rem;
        }

        .top-nav-title {
            color: #38BDF8 !important;
            font-size: 0.78rem;
            font-weight: 900;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        a {
            text-decoration: none !important;
        }

        div[data-testid="column"] [data-testid="stPageLink"] {
            border-radius: 14px !important;
            background: rgba(15, 23, 42, 0.72) !important;
            border: 1px solid rgba(51, 65, 85, 0.85) !important;
            padding: 0.25rem 0.55rem !important;
            transition: all 0.15s ease-in-out !important;
        }

        div[data-testid="column"] [data-testid="stPageLink"]:hover {
            background: rgba(56, 189, 248, 0.12) !important;
            border-color: rgba(56, 189, 248, 0.42) !important;
            transform: translateY(-1px);
        }

        div[data-testid="column"] [data-testid="stPageLink"] * {
            color: var(--clean0ps-text) !important;
            font-weight: 800 !important;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #111827 0%, #0B1120 100%) !important;
            border-right: 1px solid var(--clean0ps-border) !important;
        }

        [data-testid="stSidebar"] * {
            color: var(--clean0ps-text) !important;
        }

        [data-testid="stSidebarNav"] {
            display: none !important;
        }

        .sidebar-brand {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            padding: 1rem 0.25rem 1.25rem 0.25rem;
            margin-bottom: 0.5rem;
            border-bottom: 1px solid rgba(148, 163, 184, 0.25);
        }

        .sidebar-logo {
            width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 16px;
            background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%);
            box-shadow: 0 12px 30px rgba(37, 99, 235, 0.28);
            font-size: 1.35rem;
        }

        .sidebar-title {
            font-size: 1.25rem;
            font-weight: 900;
            color: var(--clean0ps-text-strong) !important;
            line-height: 1.1;
            letter-spacing: -0.03em;
        }

        .sidebar-subtitle {
            font-size: 0.78rem;
            color: var(--clean0ps-muted) !important;
            margin-top: 0.2rem;
        }

        .sidebar-section-label {
            font-size: 0.72rem;
            font-weight: 900;
            color: #64748B !important;
            letter-spacing: 0.08em;
            margin-top: 1.1rem;
            margin-bottom: 0.35rem;
            padding-left: 0.2rem;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] {
            background: transparent !important;
            border: none !important;
            border-radius: 14px !important;
            padding: 0.18rem 0.35rem !important;
            margin-bottom: 0.28rem !important;
            transition: all 0.15s ease-in-out !important;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"]:hover {
            background: rgba(56, 189, 248, 0.10) !important;
            transform: translateX(2px);
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] * {
            color: var(--clean0ps-text) !important;
            font-weight: 750 !important;
        }

        .sidebar-workflow-card {
            padding: 0.95rem;
            border-radius: 18px;
            background: linear-gradient(
                135deg,
                rgba(15, 23, 42, 0.96) 0%,
                rgba(30, 41, 59, 0.92) 100%
            );
            border: 1px solid rgba(51, 65, 85, 0.95);
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.18);
            margin-top: 0.45rem;
        }

        .sidebar-workflow-title {
            color: var(--clean0ps-text-strong) !important;
            font-size: 0.9rem;
            font-weight: 850;
            margin-bottom: 0.3rem;
        }

        .sidebar-workflow-text {
            color: var(--clean0ps-muted) !important;
            font-size: 0.78rem;
            line-height: 1.45;
        }

        .sidebar-status {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            padding: 0.85rem;
            border-radius: 16px;
            background-color: rgba(15, 23, 42, 0.72);
            border: 1px solid rgba(51, 65, 85, 0.85);
            margin-top: 1rem;
        }

        .sidebar-status-dot {
            width: 10px;
            height: 10px;
            border-radius: 999px;
            background-color: var(--clean0ps-green);
            box-shadow: 0 0 18px rgba(34, 197, 94, 0.75);
        }

        .sidebar-status-title {
            color: var(--clean0ps-text-strong) !important;
            font-size: 0.8rem;
            font-weight: 850;
            line-height: 1.1;
        }

        .sidebar-status-text {
            color: var(--clean0ps-muted) !important;
            font-size: 0.72rem;
            margin-top: 0.18rem;
        }

        /* Hero */
        .clean0ps-hero {
            padding: 2rem;
            border-radius: 24px;
            background:
                radial-gradient(circle at top right, rgba(56, 189, 248, 0.16) 0%, transparent 32%),
                linear-gradient(135deg, #111827 0%, #0F172A 55%, #082F49 100%);
            border: 1px solid var(--clean0ps-border);
            box-shadow: 0 22px 50px rgba(0, 0, 0, 0.35);
            margin-top: 1rem;
            margin-bottom: 1.25rem;
        }

        .clean0ps-pill {
            display: inline-block;
            padding: 0.38rem 0.78rem;
            border-radius: 999px;
            background-color: rgba(56, 189, 248, 0.14);
            color: var(--clean0ps-blue) !important;
            border: 1px solid rgba(56, 189, 248, 0.35);
            font-weight: 850;
            font-size: 0.8rem;
            margin-bottom: 0.8rem;
            letter-spacing: 0.03em;
        }

        .clean0ps-title {
            font-size: 2.5rem;
            font-weight: 900;
            color: var(--clean0ps-text-strong) !important;
            margin-bottom: 0.35rem;
            letter-spacing: -0.04em;
        }

        .clean0ps-subtitle {
            font-size: 1.08rem;
            color: var(--clean0ps-muted) !important;
            line-height: 1.65;
            max-width: 950px;
        }

        .clean0ps-section-title {
            font-size: 1.35rem;
            font-weight: 900;
            color: var(--clean0ps-text-strong) !important;
            margin-top: 1.4rem;
            margin-bottom: 0.7rem;
            letter-spacing: -0.02em;
        }

        /* Reusable modern components */
        .clean0ps-card,
        .clean0ps-panel,
        .clean0ps-download-card,
        .clean0ps-empty-state,
        .clean0ps-callout {
            border: 1px solid var(--clean0ps-border);
            box-shadow: 0 14px 32px rgba(0, 0, 0, 0.24);
        }

        .clean0ps-card {
            padding: 1.2rem;
            border-radius: 18px;
            background:
                radial-gradient(circle at top right, rgba(56, 189, 248, 0.08) 0%, transparent 34%),
                linear-gradient(135deg, #111827 0%, #1E293B 100%);
            min-height: 140px;
            margin-bottom: 1rem;
        }

        .clean0ps-card-title {
            color: var(--clean0ps-text-strong) !important;
            font-size: 1.05rem;
            font-weight: 900;
            margin-bottom: 0.45rem;
        }

        .clean0ps-card-text {
            color: var(--clean0ps-muted) !important;
            font-size: 0.95rem;
            line-height: 1.55;
        }

        .clean0ps-mini-card {
            padding: 0.95rem;
            border-radius: 16px;
            background:
                radial-gradient(circle at top right, rgba(56, 189, 248, 0.08) 0%, transparent 34%),
                linear-gradient(135deg, #111827 0%, #1E293B 100%);
            border: 1px solid var(--clean0ps-border);
            text-align: center;
            min-height: 86px;
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.22);
            margin-bottom: 0.75rem;
        }

        .clean0ps-mini-label {
            font-size: 0.76rem;
            color: var(--clean0ps-blue) !important;
            font-weight: 900;
            margin-bottom: 0.3rem;
            letter-spacing: 0.04em;
        }

        .clean0ps-mini-value {
            font-size: 0.95rem;
            color: var(--clean0ps-text-strong) !important;
            font-weight: 850;
        }

        .clean0ps-panel {
            padding: 1.15rem;
            border-radius: 18px;
            background: rgba(15, 23, 42, 0.78);
            margin-bottom: 1rem;
        }

        .clean0ps-panel-title {
            color: var(--clean0ps-text-strong) !important;
            font-weight: 900;
            font-size: 1rem;
            margin-bottom: 0.35rem;
        }

        .clean0ps-panel-text {
            color: var(--clean0ps-muted) !important;
            font-size: 0.92rem;
            line-height: 1.55;
        }

        .clean0ps-callout {
            padding: 1.05rem 1.15rem;
            border-radius: 18px;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, rgba(14, 165, 233, 0.14) 0%, rgba(37, 99, 235, 0.10) 100%);
            border-color: rgba(56, 189, 248, 0.35);
        }

        .clean0ps-callout.success {
            background: linear-gradient(135deg, rgba(34, 197, 94, 0.14) 0%, rgba(20, 83, 45, 0.16) 100%);
            border-color: rgba(34, 197, 94, 0.35);
        }

        .clean0ps-callout.warning {
            background: linear-gradient(135deg, rgba(250, 204, 21, 0.13) 0%, rgba(113, 63, 18, 0.18) 100%);
            border-color: rgba(250, 204, 21, 0.35);
        }

        .clean0ps-callout.danger {
            background: linear-gradient(135deg, rgba(248, 113, 113, 0.13) 0%, rgba(127, 29, 29, 0.18) 100%);
            border-color: rgba(248, 113, 113, 0.35);
        }

        .clean0ps-callout-title {
            color: var(--clean0ps-text-strong) !important;
            font-size: 1rem;
            font-weight: 900;
            margin-bottom: 0.3rem;
        }

        .clean0ps-callout-text {
            color: var(--clean0ps-muted) !important;
            font-size: 0.92rem;
            line-height: 1.55;
        }

        .clean0ps-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.28rem 0.65rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 900;
            letter-spacing: 0.03em;
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
        }

        .clean0ps-badge.info {
            color: var(--clean0ps-blue) !important;
            background: rgba(56, 189, 248, 0.13);
            border: 1px solid rgba(56, 189, 248, 0.34);
        }

        .clean0ps-badge.success {
            color: var(--clean0ps-green) !important;
            background: rgba(34, 197, 94, 0.13);
            border: 1px solid rgba(34, 197, 94, 0.34);
        }

        .clean0ps-badge.warning {
            color: var(--clean0ps-yellow) !important;
            background: rgba(250, 204, 21, 0.13);
            border: 1px solid rgba(250, 204, 21, 0.34);
        }

        .clean0ps-badge.danger {
            color: var(--clean0ps-red) !important;
            background: rgba(248, 113, 113, 0.13);
            border: 1px solid rgba(248, 113, 113, 0.34);
        }

        .clean0ps-stepper {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(135px, 1fr));
            gap: 0.7rem;
            margin: 0.75rem 0 1.15rem 0;
        }

        .clean0ps-step {
            padding: 0.85rem;
            border-radius: 16px;
            background: rgba(15, 23, 42, 0.72);
            border: 1px solid rgba(51, 65, 85, 0.85);
        }

        .clean0ps-step.active {
            background: rgba(56, 189, 248, 0.12);
            border-color: rgba(56, 189, 248, 0.42);
        }

        .clean0ps-step.complete {
            background: rgba(34, 197, 94, 0.10);
            border-color: rgba(34, 197, 94, 0.34);
        }

        .clean0ps-step-number {
            width: 28px;
            height: 28px;
            border-radius: 999px;
            background: rgba(56, 189, 248, 0.18);
            border: 1px solid rgba(56, 189, 248, 0.38);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: var(--clean0ps-blue) !important;
            font-size: 0.78rem;
            font-weight: 900;
            margin-bottom: 0.5rem;
        }

        .clean0ps-step-label {
            color: var(--clean0ps-text-strong) !important;
            font-size: 0.85rem;
            font-weight: 850;
        }

        .clean0ps-empty-state {
            padding: 1.25rem;
            border-radius: 18px;
            background: rgba(15, 23, 42, 0.72);
            text-align: center;
            margin: 0.8rem 0 1rem 0;
        }

        .clean0ps-empty-icon {
            font-size: 2rem;
            margin-bottom: 0.45rem;
        }

        .clean0ps-empty-title {
            color: var(--clean0ps-text-strong) !important;
            font-weight: 900;
            font-size: 1.05rem;
            margin-bottom: 0.35rem;
        }

        .clean0ps-empty-text {
            color: var(--clean0ps-muted) !important;
            font-size: 0.92rem;
            line-height: 1.55;
        }

        .clean0ps-download-card {
            padding: 1rem;
            border-radius: 18px;
            background:
                radial-gradient(circle at top right, rgba(34, 197, 94, 0.08) 0%, transparent 34%),
                linear-gradient(135deg, #111827 0%, #1E293B 100%);
            margin-bottom: 0.75rem;
        }

        .clean0ps-download-title {
            color: var(--clean0ps-text-strong) !important;
            font-size: 0.98rem;
            font-weight: 900;
            margin-bottom: 0.3rem;
        }

        .clean0ps-download-text {
            color: var(--clean0ps-muted) !important;
            font-size: 0.86rem;
            line-height: 1.45;
        }

        /* Text */
        h1, h2, h3, h4, h5, h6,
        label,
        .stMarkdown,
        .stText,
        .stCaption {
            color: var(--clean0ps-text) !important;
        }

        p {
            color: var(--clean0ps-muted) !important;
        }

        /* Inputs */
        div[data-baseweb="select"] > div {
            background-color: #111827 !important;
            border-color: var(--clean0ps-border) !important;
            color: var(--clean0ps-text) !important;
        }

        div[data-baseweb="select"] span {
            color: var(--clean0ps-text) !important;
        }

        input,
        textarea {
            background-color: #111827 !important;
            color: var(--clean0ps-text) !important;
            border-color: var(--clean0ps-border) !important;
        }

        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea {
            background-color: #111827 !important;
            color: var(--clean0ps-text) !important;
            border: 1px solid var(--clean0ps-border) !important;
            border-radius: 12px !important;
        }

        /* File uploader */
        [data-testid="stFileUploader"] section {
            background:
                radial-gradient(circle at top right, rgba(56, 189, 248, 0.09) 0%, transparent 36%),
                linear-gradient(135deg, #111827 0%, #1E293B 100%) !important;
            border: 1px solid var(--clean0ps-border) !important;
            border-radius: 18px !important;
            color: var(--clean0ps-text) !important;
        }

        [data-testid="stFileUploader"] section * {
            color: var(--clean0ps-text) !important;
        }

        [data-testid="stFileUploader"] small {
            color: var(--clean0ps-muted) !important;
        }

        [data-testid="stFileUploader"] button {
            background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%) !important;
            color: white !important;
            border-radius: 14px !important;
            font-weight: 800 !important;
        }

        /* Expanders */
        [data-testid="stExpander"] {
            background-color: rgba(17, 24, 39, 0.9) !important;
            border: 1px solid var(--clean0ps-border) !important;
            border-radius: 16px !important;
        }

        [data-testid="stExpander"] summary {
            color: var(--clean0ps-text-strong) !important;
            font-weight: 800 !important;
        }

        /* Metrics */
        [data-testid="stMetric"] {
            background:
                radial-gradient(circle at top right, rgba(56, 189, 248, 0.08) 0%, transparent 34%),
                linear-gradient(135deg, #111827 0%, #1E293B 100%);
            border: 1px solid var(--clean0ps-border);
            border-radius: 18px;
            padding: 1rem;
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.22);
        }

        [data-testid="stMetric"] label {
            color: var(--clean0ps-muted) !important;
        }

        [data-testid="stMetricValue"] {
            color: var(--clean0ps-text-strong) !important;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.4rem;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: #111827;
            border: 1px solid var(--clean0ps-border);
            border-radius: 999px;
            color: var(--clean0ps-muted);
            padding: 0.5rem 0.9rem;
        }

        .stTabs [aria-selected="true"] {
            background-color: rgba(56, 189, 248, 0.16) !important;
            color: var(--clean0ps-blue) !important;
            border-color: rgba(56, 189, 248, 0.45) !important;
        }

        /* Dataframes */
        .stDataFrame,
        [data-testid="stDataFrame"] {
            border: 1px solid var(--clean0ps-border);
            border-radius: 16px;
            overflow: hidden;
        }

        /* Buttons */
        div.stDownloadButton > button,
        div.stButton > button {
            background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 14px !important;
            font-weight: 800 !important;
            padding: 0.65rem 0.85rem !important;
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.25);
        }

        div.stDownloadButton > button:hover,
        div.stButton > button:hover {
            filter: brightness(1.08);
            border-color: rgba(255, 255, 255, 0.25) !important;
        }

        /* Alerts */
        div[data-testid="stAlert"] {
            border-radius: 16px !important;
            border: 1px solid var(--clean0ps-border) !important;
        }

        hr {
            border-color: var(--clean0ps-border) !important;
        }

        @media (prefers-color-scheme: light) {
            html,
            body,
            #root,
            .stApp,
            [data-testid="stApp"],
            [data-testid="stAppViewContainer"],
            [data-testid="stAppViewContainer"] > .main {
                background:
                    radial-gradient(circle at top left, #111827 0%, #0B1120 44%, #020617 100%) !important;
                color: var(--clean0ps-text) !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    render_sidebar()
    render_top_nav()


# --------------------------------------------------
# Existing Components
# --------------------------------------------------

def hero(title, subtitle, pill):
    st.markdown(
        f"""
        <div class="clean0ps-hero">
            <div class="clean0ps-pill">{html.escape(str(pill))}</div>
            <div class="clean0ps-title">{html.escape(str(title))}</div>
            <div class="clean0ps-subtitle">{html.escape(str(subtitle))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def section_title(text):
    st.markdown(
        f'<div class="clean0ps-section-title">{html.escape(str(text))}</div>',
        unsafe_allow_html=True
    )


def feature_card(title, text):
    st.markdown(
        f"""
        <div class="clean0ps-card">
            <div class="clean0ps-card-title">{html.escape(str(title))}</div>
            <div class="clean0ps-card-text">{html.escape(str(text))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def mini_card(label, value):
    st.markdown(
        f"""
        <div class="clean0ps-mini-card">
            <div class="clean0ps-mini-label">{html.escape(str(label))}</div>
            <div class="clean0ps-mini-value">{html.escape(str(value))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# New Modern Components
# --------------------------------------------------

def workflow_stepper(steps, active_index=0):
    items = []

    for index, step in enumerate(steps):
        if index < active_index:
            status_class = "complete"
        elif index == active_index:
            status_class = "active"
        else:
            status_class = ""

        safe_step = html.escape(str(step))

        items.append(
            '<div class="clean0ps-step ' + status_class + '">'
            '<div class="clean0ps-step-number">' + str(index + 1) + '</div>'
            '<div class="clean0ps-step-label">' + safe_step + '</div>'
            '</div>'
        )

    html_block = '<div class="clean0ps-stepper">' + ''.join(items) + '</div>'

    st.markdown(
        html_block,
        unsafe_allow_html=True
    )



def status_badge(label, status="info"):
    valid_statuses = ["info", "success", "warning", "danger"]

    if status not in valid_statuses:
        status = "info"

    st.markdown(
        f"""
        <span class="clean0ps-badge {status}">
            {html.escape(str(label))}
        </span>
        """,
        unsafe_allow_html=True
    )


def badge_row(badges):
    """
    badges format:
    [
        ("Ready", "success"),
        ("Needs Review", "warning")
    ]
    """
    badge_html = []

    for label, status in badges:
        if status not in ["info", "success", "warning", "danger"]:
            status = "info"

        badge_html.append(
            f'<span class="clean0ps-badge {status}">{html.escape(str(label))}</span>'
        )

    st.markdown(
        "".join(badge_html),
        unsafe_allow_html=True
    )


def section_callout(title, text, kind="info"):
    valid_kinds = ["info", "success", "warning", "danger"]

    if kind not in valid_kinds:
        kind = "info"

    st.markdown(
        f"""
        <div class="clean0ps-callout {kind}">
            <div class="clean0ps-callout-title">{html.escape(str(title))}</div>
            <div class="clean0ps-callout-text">{html.escape(str(text))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def info_panel(title, text):
    st.markdown(
        f"""
        <div class="clean0ps-panel">
            <div class="clean0ps-panel-title">{html.escape(str(title))}</div>
            <div class="clean0ps-panel-text">{html.escape(str(text))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def empty_state(title, text, icon="📭"):
    st.markdown(
        f"""
        <div class="clean0ps-empty-state">
            <div class="clean0ps-empty-icon">{html.escape(str(icon))}</div>
            <div class="clean0ps-empty-title">{html.escape(str(title))}</div>
            <div class="clean0ps-empty-text">{html.escape(str(text))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def download_card(title, text):
    st.markdown(
        f"""
        <div class="clean0ps-download-card">
            <div class="clean0ps-download-title">{html.escape(str(title))}</div>
            <div class="clean0ps-download-text">{html.escape(str(text))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def metric_card(label, value, caption=""):
    st.markdown(
        f"""
        <div class="clean0ps-mini-card">
            <div class="clean0ps-mini-label">{html.escape(str(label))}</div>
            <div class="clean0ps-mini-value">{html.escape(str(value))}</div>
            <div class="clean0ps-card-text" style="font-size:0.78rem;margin-top:0.35rem;">
                {html.escape(str(caption))}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# Production Helpers
# --------------------------------------------------

def privacy_notice():
    section_callout(
        title="Privacy notice",
        text=(
            "Files are processed during the current app session. Clean0ps does not permanently store "
            "uploaded files by default. Avoid uploading sensitive data unless you trust the environment "
            "where this app is running."
        ),
        kind="warning"
    )


def reset_workflow_button(label="Reset Workflow"):
    if st.button(label):
        st.session_state.clear()
        st.rerun()

