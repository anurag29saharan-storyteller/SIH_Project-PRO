"""
System Architecture, DuPont/Campbell Institute Methodology, and High-Energy Catalog.
"""
import streamlit as st
from src.domain.constants import HIGH_ENERGY_SOURCES, CONTROL_FAILURE_MARKERS


def render_methodology_view(current_theme: str = "dark"):
    st.subheader("?? SIF Prevention Methodology & System Architecture")

    flow_cols = st.columns(5)
    steps = [
        "?? Incident<br>Report Input",
        "?? NLP Engine<br>(Rule + LLM)",
        "? High-Energy<br>Source Check",
        "?? Barrier / Control<br>Failure Check",
        "?? SIF Score &<br>Escalation Plan"
    ]
    for col, step in zip(flow_cols, steps):
        col.markdown(f"<div class='flow-box'>{step}</div>", unsafe_allow_html=True)

    st.write("")
    st.markdown(
        """
### Core Methodology ? High Energy + Failed Direct Control = SIF Precursor

According to the **Campbell Institute** and **DuPont SIF Prevention Framework**, safety incidents cannot be treated equally. 
Low-severity incidents and Serious Injury/Fatality (SIF) precursors stem from fundamentally different risk profiles:

1. **High-Energy Source (Hazard Potential):** The presence of sufficient hazardous energy (gravity, electrical, chemical, pressure, kinetic) that could result in life-threatening or fatal trauma.
2. **Direct Barrier / Control Status:** Whether a physical or engineered barrier was absent, compromised, failed, or bypassed.

When **High Energy** is coupled with a **Control Failure**, the incident is a **Critical SIF Precursor** requiring immediate stop-work and hierarchy-of-controls escalation.
        """
    )

    st.divider()

    st.markdown("### ? High-Energy Hazard Categories Monitored")
    cols = st.columns(2)
    items = list(HIGH_ENERGY_SOURCES.items())
    half = len(items) // 2

    with cols[0]:
        for name, cfg in items[:half]:
            with st.expander(f"? {name} (Weight: {cfg['weight']}/10)"):
                st.markdown(f"**Description:** {cfg.get('description', '')}")
                st.markdown(f"**Monitored Keywords:** `{', '.join(cfg['keywords'][:8])}...`")

    with cols[1]:
        for name, cfg in items[half:]:
            with st.expander(f"? {name} (Weight: {cfg['weight']}/10)"):
                st.markdown(f"**Description:** {cfg.get('description', '')}")
                st.markdown(f"**Monitored Keywords:** `{', '.join(cfg['keywords'][:8])}...`")

    st.divider()

    st.markdown("### ??? Barrier & Control Failure Indicators")
    st.markdown(f"The platform scans for over **{len(CONTROL_FAILURE_MARKERS)}** direct control compromise phrases in English and Hindi, including:")
    st.code(", ".join(CONTROL_FAILURE_MARKERS[:25]) + "...")
