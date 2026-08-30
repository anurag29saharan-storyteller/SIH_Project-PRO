"""
Batch Incident Analytics, Geospatial Heatmap, and Trend Risk Forecasting View.
"""
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from src.database import get_db, ReportRepository
from src.engines import LocalEngine, TrendForecastingEngine
from src.ui.components import render_metric_card
from src.ui.maps import render_geospatial_heatmap
from src.utils.pdf_exporter import generate_batch_summary_pdf


def render_batch_analytics_view(current_theme: str = "dark"):
    st.subheader("?? Enterprise Batch Incident Analytics & Predictive Risk")
    st.caption("Analyze historical near-miss datasets, view geospatial risk density, and forecast forward SIF probabilities.")

    up1, up2 = st.columns([2, 1])
    with up1:
        uploaded_file = st.file_uploader("Upload CSV of Incident Reports (Columns: Narrative, Location, Date)", type=["csv"])
    with up2:
        st.write("")
        st.write("")
        if st.button("?? Load 150-Record Oilfield Demo Dataset", use_container_width=True):
            with st.spinner("Seeding database with 150 realistic oilfield incident logs..."):
                with get_db() as session:
                    repo = ReportRepository(session)
                    repo.seed_demo_data(count=150)
                st.success("Successfully seeded 150 records into the persistent database!")
                st.rerun()

    # Load from DB or Uploaded File
    df = None
    if uploaded_file is not None:
        try:
            raw_df = pd.read_csv(uploaded_file)
            st.info(f"Loaded uploaded file with {len(raw_df)} rows. Processing SIF rules...")
            
            narrative_col = next((c for c in raw_df.columns if c.lower() in ["narrative", "description", "text", "incident"]), None)
            if narrative_col:
                engine = LocalEngine()
                results = []
                for _, row in raw_df.iterrows():
                    res = engine.analyze(str(row[narrative_col]))
                    first_energy = res.matched_energy[0] if res.matched_energy else "General Safety"
                    results.append({
                        "Date": row.get("Date", datetime.date.today()),
                        "Location": row.get("Location", "Field Asset"),
                        "Narrative": str(row[narrative_col]),
                        "Risk_Score": res.score,
                        "Category": res.category,
                        "Incident_Type": first_energy,
                        "Detected_Energy": ", ".join(res.matched_energy),
                        "Control_Failures": ", ".join(res.matched_controls),
                        "Engine": "Local Engine"
                    })
                df = pd.DataFrame(results)
            else:
                st.error("Uploaded CSV must have a 'Narrative', 'Description', or 'Text' column.")
        except Exception as e:
            st.error(f"Error parsing uploaded file: {e}")

    else:
        # Load from persistent database
        with get_db() as session:
            repo = ReportRepository(session)
            df = repo.get_all_reports_dataframe()

    if df is not None and not df.empty:
        total_reports = len(df)
        crit_pct = (df["Category"] == "Critical SIF Precursor").mean() * 100.0 if "Category" in df.columns else 0.0
        avg_score = df["Risk_Score"].mean() if "Risk_Score" in df.columns else 0.0
        top_hazard = df["Incident_Type"].mode()[0] if "Incident_Type" in df.columns and not df["Incident_Type"].mode().empty else "N/A"

        st.divider()

        # KPI Tiles
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            render_metric_card("Total Reports", total_reports, "Historical Incidents")
        with k2:
            render_metric_card("Critical SIF Precursors", f"{crit_pct:.1f}%", "High-Energy Failures")
        with k3:
            render_metric_card("Avg Risk Score", f"{avg_score:.1f}%", "Site Severity Baseline")
        with k4:
            render_metric_card("Top Hazard Type", top_hazard, "Dominant Energy Vector")

        st.write("")

        # 4 Plotly Charts Grid
        font_color = "#ffffff" if current_theme == "dark" else "#0f172a"

        c1, c2 = st.columns(2)
        with c1:
            fig_pie = px.pie(
                df,
                names="Incident_Type",
                title="<b>Hazard Category Distribution</b>",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color=font_color))
            st.plotly_chart(fig_pie, use_container_width=True)

        with c2:
            fig_hist = px.histogram(
                df,
                x="Risk_Score",
                nbins=16,
                title="<b>SIF Risk Score Frequency Distribution</b>",
                color="Category",
                color_discrete_map={
                    "Critical SIF Precursor": "#ff5c5c",
                    "Potential Precursor / Elevated Risk": "#ffcc4d",
                    "Routine Safety Observation": "#5fd88f"
                }
            )
            fig_hist.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color=font_color))
            st.plotly_chart(fig_hist, use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            loc_counts = df.groupby("Location")["Risk_Score"].mean().sort_values(ascending=True).reset_index()
            fig_bar = px.bar(
                loc_counts,
                x="Risk_Score",
                y="Location",
                orientation="h",
                title="<b>Average Risk Score by Facility / Asset</b>",
                color="Risk_Score",
                color_continuous_scale="Reds"
            )
            fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color=font_color))
            st.plotly_chart(fig_bar, use_container_width=True)

        with c4:
            trend_df = df.copy()
            trend_df["Date"] = pd.to_datetime(trend_df["Date"], errors="coerce")
            trend_df = trend_df.dropna(subset=["Date"]).sort_values("Date")
            weekly = trend_df.groupby(trend_df["Date"].dt.to_period("W"))["Risk_Score"].mean().reset_index()
            weekly["Date"] = weekly["Date"].astype(str)

            fig_line = px.line(
                weekly,
                x="Date",
                y="Risk_Score",
                title="<b>Weekly Average Risk Score Trend</b>",
                markers=True,
                line_shape="spline"
            )
            fig_line.update_traces(line_color="#ff5c5c", marker=dict(size=8, color="#ffb84d"))
            fig_line.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color=font_color))
            st.plotly_chart(fig_line, use_container_width=True)

        st.divider()

        # Geospatial Heatmap
        st.subheader("??? Facility Risk Density & Geospatial Heatmap")
        st.caption("Interactive Leaflet map showing Oil India facilities, incident volumes, and risk severity clusters.")
        render_geospatial_heatmap(df, theme=current_theme)

        st.divider()

        # Trend Risk Forecasting Module
        st.subheader("?? Predictive SIF Risk Score Forecasting (Prophet / ARIMA)")
        st.caption("Projects next 14 days risk score baseline and flags upward trend anomalies.")

        forecast_engine = TrendForecastingEngine()
        forecast_points = forecast_engine.forecast_risk_trend(df, forecast_days=14)

        if forecast_points:
            f_df = pd.DataFrame([p.model_dump() for p in forecast_points])
            
            fig_forecast = px.line(
                f_df,
                x="date",
                y="predicted_score",
                title="<b>Projected Forward 14-Day SIF Risk Trajectory</b>",
                markers=True
            )
            fig_forecast.add_scatter(
                x=f_df["date"],
                y=f_df["upper_bound"],
                mode="lines",
                name="90% Upper Bound",
                line=dict(width=0),
                showlegend=False
            )
            fig_forecast.add_scatter(
                x=f_df["date"],
                y=f_df["lower_bound"],
                mode="lines",
                name="90% Confidence Interval",
                fill="tonexty",
                fillcolor="rgba(255, 92, 92, 0.15)",
                line=dict(width=0)
            )
            fig_forecast.update_traces(line_color="#38bdf8", selector=dict(name="predicted_score"))
            fig_forecast.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color=font_color))
            st.plotly_chart(fig_forecast, use_container_width=True)
            
            anomalies = [p for p in forecast_points if p.is_anomaly]
            if anomalies:
                st.warning(f"?? Predictive Model Alert: {len(anomalies)} forecasted dates cross the critical risk threshold (>=80%). Proactive safety intervention recommended.")
        else:
            st.info("Insufficient longitudinal data for predictive time-series extrapolation.")

        st.divider()

        # Executive Batch PDF Export
        st.subheader("?? Export Executive Batch Summary")
        batch_pdf = generate_batch_summary_pdf(df)
        st.download_button(
            label="?? Download Executive SIF Audit Report (PDF)",
            data=batch_pdf,
            file_name=f"Executive_SIF_Summary_OIL_{datetime.date.today()}.pdf",
            mime="application/pdf"
        )

        st.write("")
        st.markdown("**Detailed Incident Log Records:**")
        st.dataframe(df.sort_values(by="Risk_Score", ascending=False).head(30), use_container_width=True)

    else:
        st.info("No reports found in database. Click **Load 150-Record Oilfield Demo Dataset** above or upload a CSV to view analytics.")
