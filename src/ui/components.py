"""
Reusable UI widgets, metric cards, Plotly charts, and emergency response banners.
"""
from typing import List, Dict, Any, Optional
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.domain.constants import HIGH_ENERGY_SOURCES, SEVERITY_LEVELS, EMERGENCY_HELPLINES


def render_header():
    st.markdown(
        """
        <div style='text-align:center; padding:6px 0 2px;'>
            <div style='
                font-size:2.1rem; font-weight:900; letter-spacing:6px;
                background: linear-gradient(90deg, #ff5c5c, #ffb84d, #5fd88f, #4dc8ff, #ff5c5c);
                background-size: 300% auto;
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                background-clip: text;
                animation: shine 6s linear infinite;
            '>
                OMEGA
            </div>
            <div style='color:#aab0bb; font-style:italic; font-size:0.95rem; margin-top:2px;'>
                “Every near-miss is a warning whispered before disaster has to shout.”
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_metric_card(title: str, value: Any, subtitle: str = "", delta: Optional[str] = None):
    """Renders a styled metric card."""
    delta_html = f"<div style='color:#5fd88f; font-size:0.8rem; font-weight:600; margin-top:2px;'>{delta}</div>" if delta else ""
    st.markdown(
        f"""
<div class='metric-card'>
    <div class='subtitle'>{subtitle or title}</div>
    <h3>{value}</h3>
    {delta_html}
</div>
        """,
        unsafe_allow_html=True
    )


def render_gauge_chart(score: int, theme: str = "dark") -> go.Figure:
    """Generates a calibrated Plotly SIF Risk Score Gauge."""
    color = "#ff5c5c" if score >= 80 else "#ffcc4d" if score >= 50 else "#5fd88f"
    font_color = "#ffffff" if theme == "dark" else "#0f172a"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "%", "font": {"size": 42, "color": font_color, "family": "Segoe UI"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": font_color, "tickwidth": 1.5},
            "bar": {"color": color, "thickness": 0.3},
            "steps": [
                {"range": [0, 50], "color": "rgba(22, 163, 74, 0.25)"},
                {"range": [50, 80], "color": "rgba(217, 119, 6, 0.25)"},
                {"range": [80, 100], "color": "rgba(220, 38, 38, 0.35)"},
            ],
            "threshold": {"line": {"color": font_color, "width": 3}, "value": score},
        },
        title={"text": "<b>SIF Risk Potential</b>", "font": {"color": font_color, "size": 16}},
    ))
    fig.update_layout(
        height=280,
        margin=dict(l=25, r=25, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def render_factor_chart(matched_energy: List[str], matched_controls: List[str], theme: str = "dark") -> Optional[go.Figure]:
    """Renders a horizontal contribution breakdown chart."""
    rows = []
    for e in matched_energy:
        weight = HIGH_ENERGY_SOURCES.get(e, {}).get("weight", 8)
        rows.append({"Factor": f"? {e}", "Contribution": weight, "Type": "High-Energy Source"})
    for c in matched_controls:
        rows.append({"Factor": f"?? {c}", "Contribution": 6, "Type": "Control / Barrier Failure"})

    if not rows:
        return None

    import pandas as pd
    fdf = pd.DataFrame(rows).sort_values("Contribution", ascending=True)
    font_color = "#ffffff" if theme == "dark" else "#0f172a"

    fig = px.bar(
        fdf,
        x="Contribution",
        y="Factor",
        color="Type",
        orientation="h",
        color_discrete_map={
            "High-Energy Source": "#ffb84d",
            "Control / Barrier Failure": "#ff5c5c"
        },
        title="<b>Factor Contribution Breakdown</b>",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=font_color),
        height=max(240, 48 * len(rows)),
        showlegend=True,
        xaxis_title="",
        yaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def render_coverage_donut(matched_energy: List[str], theme: str = "dark") -> go.Figure:
    """Renders a donut chart showing triggered energy hazard categories."""
    total = len(HIGH_ENERGY_SOURCES)
    triggered = len(matched_energy)
    font_color = "#ffffff" if theme == "dark" else "#0f172a"

    fig = px.pie(
        names=["Triggered", "Not Triggered"],
        values=[triggered, total - triggered],
        hole=0.68,
        color=["Triggered", "Not Triggered"],
        color_discrete_map={
            "Triggered": "#ffb84d",
            "Not Triggered": "rgba(100, 116, 139, 0.25)"
        },
        title="<b>Hazard Breadth Triggered</b>",
    )
    fig.update_traces(textinfo="none", hoverinfo="label+value")
    fig.add_annotation(
        text=f"<b>{triggered}</b>/{total}",
        showarrow=False,
        font=dict(size=26, color=font_color)
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=font_color),
        showlegend=False,
        height=280,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


def render_emergency_banner(is_critical: bool = False):
    """Renders the India emergency hotlines & Oil India HSE control room contacts."""
    if is_critical:
        helpline_html = "".join(
            f"<div class='helpline-box'><span>{h['icon']} {h['label']}</span>"
            f"<span class='helpline-num'>{h['number']}</span></div>"
            for h in EMERGENCY_HELPLINES
        )
        st.markdown(
            f"""
<div class='helpline-critical'>
    <div style='font-size:1.1rem; font-weight:800; color:#ef4444; margin-bottom:6px;'>
        ?? CRITICAL SIF PRECURSOR DETECTED ? IMMEDIATE STOP-WORK & ESCALATION
    </div>
    <p style='color:#cbd5e1; margin:0 0 10px 0; font-size:0.9rem;'>
        This incident involves unmitigated high energy and a barrier failure. 
        If this reflects an active condition, halt work and notify site safety supervisor:
    </p>
    {helpline_html}
</div>
            """,
            unsafe_allow_html=True
        )


def render_token_tracker(prompt_tokens: int, completion_tokens: int, cost_usd: float, provider: str):
    """Displays API token consumption & cost in the sidebar."""
    st.markdown(
        f"""
<div class='token-card'>
    <div><b>AI Provider:</b> {provider}</div>
    <div><b>Tokens:</b> {prompt_tokens} in / {completion_tokens} out ({prompt_tokens + completion_tokens} tot)</div>
    <div><b>Estimated Cost:</b> ${cost_usd:.6f} USD</div>
</div>
        """,
        unsafe_allow_html=True
    )


def render_chips(items: List[str], chip_type: str = "chip-energy") -> str:
    """Returns HTML formatted chip tags."""
    if not items:
        return "<i style='color:#888;'>None detected</i>"
    return "".join(f"<span class='chip {chip_type}'>{item}</span>" for item in items)
