"""
Real-Time SIF Precursor Live Analyzer View with Multi-Engine AI,
Persistent DB Storage, Semantic Similarity, and PDF Export.
"""
import streamlit as st
import datetime
from src.domain.constants import OIL_INDIA_LOCATIONS, SEVERITY_LEVELS
from src.domain.schemas import AnalysisResultSchema
from src.engines import LocalEngine, LLMEngine, SemanticSearchEngine
from src.database import get_db, ReportRepository
from src.utils.security import sanitize_text
from src.utils.pdf_exporter import generate_incident_pdf
from src.ui.components import (
    render_gauge_chart,
    render_factor_chart,
    render_coverage_donut,
    render_chips,
    render_emergency_banner
)


def render_live_analyzer_view(current_theme: str = "dark", semantic_engine: SemanticSearchEngine = None):
    st.subheader("?? Real-Time SIF Precursor Live Analyzer")
    st.caption("Campbell Institute & DuPont Barrier-Based Triage for Unsafe Acts, Conditions & Near-Misses")

    # Quick scenario loader buttons
    st.markdown("**? Quick Test Scenarios:**")
    q1, q2, q3, q4 = st.columns(4)
    if q1.button("?? Scaffold Fall (High Risk)", use_container_width=True):
        st.session_state["report_input"] = "Worker observed on 8-meter scaffolding without safety harness tie-off, no green inspection tag on platform."
    if q2.button("? Gas Leak / H2S (Critical)", use_container_width=True):
        st.session_state["report_input"] = "H2S gas leak detected near tank farm manifold, audible alarm failed to sound because sensor was bypassed."
    if q3.button("??? Crane Rigging Failure", use_container_width=True):
        st.session_state["report_input"] = "Crane wire snapped while lifting 4-ton mud pump over personnel walkway, no signal person or banksman present."
    if q4.button("?? Routine Housekeeping", use_container_width=True):
        st.session_state["report_input"] = "Discarded empty plastic water bottles and paper cups found near workshop entrance."

    # Input Form
    col_input, col_meta = st.columns([3, 1])
    with col_meta:
        location = st.selectbox("Facility / Site Location", list(OIL_INDIA_LOCATIONS.keys()), index=0)
        engine_choice = st.selectbox(
            "AI Inference Engine",
            [
                "? Local Rule Engine (Instant & Offline)",
                "?? OpenAI (GPT-4o-mini)",
                "?? Anthropic (Claude 3 Haiku)",
                "?? Local Ollama (Llama 3)",
                "?? HuggingFace Zero-Shot"
            ],
            index=0
        )

    with col_input:
        report_text = st.text_area(
            "Describe the Incident / Near-Miss / Observation Narrative:",
            height=130,
            placeholder="e.g. Crane load swung violently near well pad A, worker bypassed barricade without safety harness...",
            key="report_input"
        )
        char_count = len(report_text)
        st.caption(f"Character count: {char_count}/5000")

    analyze_clicked = st.button("?? Analyze Incident Risk & Barriers", type="primary", use_container_width=True)

    if analyze_clicked:
        clean_text = sanitize_text(report_text)
        if not clean_text or len(clean_text) < 5:
            st.warning("?? Please provide a detailed incident narrative to analyze.")
            return

        # Determine engine
        if "OpenAI" in engine_choice:
            engine = LLMEngine(provider="openai")
        elif "Anthropic" in engine_choice or "Claude" in engine_choice:
            engine = LLMEngine(provider="anthropic")
        elif "Ollama" in engine_choice:
            engine = LLMEngine(provider="ollama")
        elif "HuggingFace" in engine_choice:
            engine = LLMEngine(provider="huggingface")
        else:
            engine = LocalEngine()

        with st.spinner("Executing energy & barrier failure analysis..."):
            result = engine.analyze(clean_text)
            
            # Save to persistent database
            with get_db() as session:
                repo = ReportRepository(session)
                saved_report = repo.create_report(
                    narrative=clean_text,
                    location=location,
                    analysis_data=result,
                    submitter_id="hse_officer"
                )
                report_id = saved_report.id

            # Update session accumulator
            st.session_state["session_tokens"] = st.session_state.get("session_tokens", 0) + result.total_tokens
            st.session_state["session_cost"] = st.session_state.get("session_cost", 0.0) + result.cost_usd
            st.session_state["latest_result"] = result
            st.session_state["latest_text"] = clean_text
            st.session_state["latest_location"] = location
            st.session_state["latest_id"] = report_id

    # Display Results if available
    if "latest_result" in st.session_state:
        res = st.session_state["latest_result"]
        rep_text = st.session_state["latest_text"]
        rep_loc = st.session_state["latest_location"]
        rep_id = st.session_state["latest_id"]

        info = SEVERITY_LEVELS.get(res.category, {"pill": "pill-caution", "emoji": "??"})
        n_energy = len(res.matched_energy)
        n_controls = len(res.matched_controls)

        st.divider()

        # Header Row
        head_l, head_r = st.columns([2, 1])
        with head_l:
            st.markdown(f"<span class='{info['pill']}'>{info['emoji']} {res.category}</span>", unsafe_allow_html=True)
        with head_r:
            badge_text = f"?? {res.engine_name}"
            if res.used_fallback:
                badge_text += f" (Fallback: {res.fallback_reason})"
            st.markdown(f"<div style='text-align:right; color:#8b949e; font-size:0.85rem;'>{badge_text} ? {res.latency_ms:.1f}ms</div>", unsafe_allow_html=True)

        st.write("")

        # Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("SIF Risk Score", f"{res.score}%")
        m2.metric("? High-Energy Sources", n_energy)
        m3.metric("?? Barrier Failures", n_controls)
        m4.metric("AI Execution Latency", f"{res.latency_ms:.1f} ms")

        st.write("")

        # Visualizations
        v1, v2, v3 = st.columns([1.1, 1.3, 1])
        with v1:
            st.plotly_chart(render_gauge_chart(res.score, theme=current_theme), use_container_width=True)
        with v2:
            fchart = render_factor_chart(res.matched_energy, res.matched_controls, theme=current_theme)
            if fchart is not None:
                st.plotly_chart(fchart, use_container_width=True)
            else:
                st.info("No high-energy sources or control failures detected in this text.")
        with v3:
            st.plotly_chart(render_coverage_donut(res.matched_energy, theme=current_theme), use_container_width=True)

        # Chips breakdown
        d1, d2 = st.columns(2)
        with d1:
            st.markdown("**? High-Energy Sources Detected**")
            st.markdown(render_chips(res.matched_energy, "chip-energy"), unsafe_allow_html=True)
        with d2:
            st.markdown("**?? Control / Barrier Failures Detected**")
            st.markdown(render_chips(res.matched_controls, "chip-control"), unsafe_allow_html=True)

        st.write("")

        # Corrective Actions Checklist
        st.markdown("**??? Recommended Immediate Corrective Actions (Hierarchy of Controls)**")
        for i, act in enumerate(res.corrective_actions):
            st.markdown(f"- **[{i+1}]** {act}")

        # Emergency Escalation Banner
        if res.score >= 80 or res.category == "Critical SIF Precursor":
            render_emergency_banner(is_critical=True)

        st.divider()

        # Semantic Similarity Drawer
        st.subheader("?? Semantically Similar Past Incidents in Database")
        with get_db() as session:
            repo = ReportRepository(session)
            all_reports = repo.get_recent_reports(limit=100)

        if semantic_engine and all_reports:
            semantic_engine.index_reports(all_reports)
            matches = semantic_engine.find_similar(rep_text, top_k=3)
            
            if matches:
                cols = st.columns(len(matches))
                for col, match in zip(cols, matches):
                    with col:
                        st.markdown(
                            f"""
<div class='similar-card'>
    <div style='font-size:0.85rem; font-weight:700; color:#3b82f6;'>
        Match: {match.similarity_score}% ? ID #{match.report_id}
    </div>
    <div style='font-size:0.8rem; color:#8b949e; margin:2px 0;'>
        ?? {match.location} | <b>{match.category}</b> ({match.score}%)
    </div>
    <div style='font-size:0.82rem; font-style:italic; margin-top:4px;'>
        "{match.snippet}"
    </div>
</div>
                            """,
                            unsafe_allow_html=True
                        )
            else:
                st.caption("No closely matching historical incidents found in the database.")
        else:
            st.caption("Load or seed historical reports to view semantic similarities.")

        st.write("")

        # PDF Export Button
        st.subheader("?? Export Formal SIF Investigation Document")
        pdf_bytes = generate_incident_pdf(
            report_text=rep_text,
            analysis=res.model_dump(),
            location=rep_loc,
            report_id=rep_id
        )
        st.download_button(
            label="?? Download SIF Assessment PDF Report",
            data=pdf_bytes,
            file_name=f"SIF_Assessment_Report_OIL_{rep_id:05d}.pdf",
            mime="application/pdf",
            type="primary"
        )
