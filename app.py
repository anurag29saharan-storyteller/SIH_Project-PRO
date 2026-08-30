"""
SIF Precursor AI Platform 🛢️ Enterprise Production Application
Oil India Limited (Smart India Hackathon Project)
"""
import streamlit as st
import datetime

# 1. Page Configuration
st.set_page_config(
    page_title="SIF AI Platform | Oil India",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Lazy / Safe Imports
from src.utils.config import get_config
from src.utils.logger import get_logger
from src.utils.security import verify_pin
from src.database import init_db, get_db, ReportRepository
from src.engines import SemanticSearchEngine
from src.ui.styles import get_custom_css
from src.ui.components import render_header, render_token_tracker
from src.ui.views import (
    render_live_analyzer_view,
    render_batch_analytics_view,
    render_history_view,
    render_methodology_view
)
from src.domain.constants import EMERGENCY_HELPLINES

logger = get_logger("app")
config = get_config()

# 3. Initialize Persistent Database
try:
    init_db()
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")

# 4. Session State Initialization
if "theme" not in st.session_state:
    st.session_state["theme"] = config.default_theme
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = not config.auth_enabled
if "session_tokens" not in st.session_state:
    st.session_state["session_tokens"] = 0
if "session_cost" not in st.session_state:
    st.session_state["session_cost"] = 0.0
if "semantic_engine" not in st.session_state:
    st.session_state["semantic_engine"] = SemanticSearchEngine()

# 5. Apply Dynamic Custom CSS Theme
st.markdown(get_custom_css(st.session_state["theme"]), unsafe_allow_html=True)

# 6. Authentication Gate
if not st.session_state["authenticated"]:
    render_header()
    st.markdown("<br/>", unsafe_allow_html=True)
    col_l, col_center, col_r = st.columns([1, 1.2, 1])
    with col_center:
        st.markdown("### 🔐 Oil India HSE Security Gate")
        st.info("Enter authorized Security PIN to access SIF Triage & Intelligence Platform.")
        pin_input = st.text_input("Enter Access PIN:", type="password", placeholder="Default: 1959")
        if st.button("Unlock Dashboard", type="primary", use_container_width=True):
            if verify_pin(pin_input, config.default_pin):
                st.session_state["authenticated"] = True
                st.success("Access granted.")
                st.rerun()
            else:
                st.error("Invalid security PIN. Please contact Oil India HSE admin.")
    st.stop()

# 7. Sidebar Navigation & Global Controls
with st.sidebar:
    st.markdown("## 🛢️ Oil India Limited")
    st.caption("SIF AI Intelligence & Precursor Detection")
    st.divider()

    # Theme Switcher
    st.markdown("### 🎨 Display Preferences")
    current_is_dark = st.session_state["theme"] == "dark"
    theme_toggle = st.toggle("🌙 Dark Mode", value=current_is_dark)
    new_theme = "dark" if theme_toggle else "light"
    if new_theme != st.session_state["theme"]:
        st.session_state["theme"] = new_theme
        st.rerun()

    st.divider()

    # Database Summary Metric
    with get_db() as session:
        repo = ReportRepository(session)
        kpis = repo.get_kpi_summary()
    st.metric("Total Incident Logs in DB", kpis["total_reports"])
    if kpis["total_reports"] > 0:
        st.caption(f"⚠️ {kpis['critical_pct']:.1f}% Critical Precursor Rate")

    st.divider()

    # LLM API Token & Cost Tracker
    st.markdown("### 🤖 Session AI Consumption")
    render_token_tracker(
        prompt_tokens=st.session_state["session_tokens"] // 2,
        completion_tokens=st.session_state["session_tokens"] // 2,
        cost_usd=st.session_state["session_cost"],
        provider="Multi-Engine Orchestrator"
    )

    st.divider()

    # Emergency Contacts
    st.markdown("### 🆘 Emergency Contacts")
    for h in EMERGENCY_HELPLINES:
        st.markdown(
            f"<div class='helpline-box'><span>{h['icon']} {h['label']}</span>"
            f"<span class='helpline-num'>{h['number']}</span></div>",
            unsafe_allow_html=True
        )

    st.divider()
    st.caption("v2.0.0 Enterprise 🚀 Smart India Hackathon")

# 8. Main Brand Header
render_header()
st.title("🛢️ Smart SIF Precursor Detection & Prevention Platform")
st.markdown(
    "Domain-grounded AI/NLP engine flagging **Serious Injury & Fatality (SIF) precursors** "
    "in unsafe acts, unsafe conditions, and near-miss reports — before they escalate to catastrophe."
)

# 9. Main Application Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Live Analyzer",
    "📊 Batch Analytics & Forecasts",
    "🗄️ Database Explorer & Audit",
    "📖 SIF Methodology & Guide"
])

with tab1:
    render_live_analyzer_view(
        current_theme=st.session_state["theme"],
        semantic_engine=st.session_state["semantic_engine"]
    )

with tab2:
    render_batch_analytics_view(current_theme=st.session_state["theme"])

with tab3:
    render_history_view(current_theme=st.session_state["theme"])

with tab4:
    render_methodology_view(current_theme=st.session_state["theme"])
