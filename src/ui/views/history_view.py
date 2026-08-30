"""
Persistent Database Explorer, Incident Search, and Audit Trail View.
"""
import streamlit as st
import pandas as pd
from src.database import get_db, ReportRepository
from src.domain.constants import OIL_INDIA_LOCATIONS
from src.utils.pdf_exporter import generate_incident_pdf


def render_history_view(current_theme: str = "dark"):
    st.subheader("?? Persistent Database Explorer & Audit Records")
    st.caption("All reports and AI analysis results are permanently saved in SQLite / PostgreSQL via SQLAlchemy.")

    with get_db() as session:
        repo = ReportRepository(session)
        df = repo.get_all_reports_dataframe()

    if df.empty:
        st.info("Database is currently empty. Analyze new reports or load demo data from the Batch Analytics tab.")
        return

    # Filter Bar
    f1, f2, f3, f4 = st.columns([1.5, 1.5, 1.5, 2])
    with f1:
        loc_filter = st.selectbox("Filter Location", ["All Locations"] + list(OIL_INDIA_LOCATIONS.keys()), index=0)
    with f2:
        cat_filter = st.multiselect(
            "Filter Category",
            ["Critical SIF Precursor", "Potential Precursor / Elevated Risk", "Routine Safety Observation"],
            default=["Critical SIF Precursor", "Potential Precursor / Elevated Risk", "Routine Safety Observation"]
        )
    with f3:
        min_score = st.slider("Min Risk Score", 0, 100, 0, 5)
    with f4:
        search_term = st.text_input("Search Narrative Keywords", placeholder="e.g. crane, scaffold, leak...")

    # Apply Filters
    filtered = df.copy()
    if loc_filter != "All Locations":
        filtered = filtered[filtered["Location"] == loc_filter]
    if cat_filter:
        filtered = filtered[filtered["Category"].isin(cat_filter)]
    if min_score > 0:
        filtered = filtered[filtered["Risk_Score"] >= min_score]
    if search_term.strip():
        term = search_term.strip().lower()
        filtered = filtered[filtered["Narrative"].str.lower().str.contains(term)]

    st.write(f"Showing **{len(filtered)}** of **{len(df)}** total reports in database.")

    # Actions row
    act1, act2 = st.columns([2, 1])
    with act1:
        st.download_button(
            label="?? Export Filtered Records (CSV)",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name="oil_india_sif_records.csv",
            mime="text/csv"
        )
    with act2:
        if st.button("??? Truncate & Clear Database", type="secondary"):
            with get_db() as session:
                repo = ReportRepository(session)
                repo.clear_all()
            st.success("Database records truncated.")
            st.rerun()

    st.write("")
    st.dataframe(filtered.sort_values("Risk_Score", ascending=False), use_container_width=True)

    # Detailed Expander for top results
    st.markdown("### 📋 Record Inspector")
    for _, row in filtered.head(5).iterrows():
        rep_id = row.get("Report_ID", "N/A")
        loc = row.get("Location", "Field")
        score_val = row.get("Risk_Score", 0)
        cat_val = row.get("Category", "Observation")
        narr_val = row.get("Narrative", "")
        energy_val = row.get("Detected_Energy", "None")
        ctrl_val = row.get("Control_Failures", "None")
        eng_val = row.get("Engine", "Local Engine")
        stat_val = row.get("Status", "TRIAGED")

        with st.expander(f"Report #{rep_id} · {loc} · Score: {score_val}% ({cat_val})"):
            st.markdown(f"**Narrative:** *\"{narr_val}\"*")
            st.markdown(f"**⚡ High-Energy Sources:** `{energy_val}`")
            st.markdown(f"**🛑 Control Failures:** `{ctrl_val}`")
            st.markdown(f"**Engine Used:** `{eng_val}` | **Status:** `{stat_val}`")
