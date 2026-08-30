"""
Geospatial Risk Heatmap Component using Folium & Leaflet.
Visualizes facility locations, incident densities, and site-level SIF risks.
"""
from typing import Dict, Any, Optional
import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap
import streamlit as st
from src.domain.constants import OIL_INDIA_LOCATIONS


def render_geospatial_heatmap(df: pd.DataFrame, theme: str = "dark"):
    """
    Renders an interactive Folium map centered on Oil India operations
    with risk-weighted circle markers and facility popups.
    """
    # Default center: Duliajan, Assam
    center_lat, center_lon = 27.3591, 95.3182
    
    # Choose base tiles based on theme
    tiles = "CartoDB dark_matter" if theme == "dark" else "CartoDB positron"
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=7,
        tiles=tiles,
        control_scale=True
    )

    heat_data = []
    
    # Calculate per-location statistics from df if present
    loc_stats = {}
    if not df.empty and "Location" in df.columns:
        for loc_name, group in df.groupby("Location"):
            avg_risk = group["Risk_Score"].mean() if "Risk_Score" in group.columns else 50
            crit_count = (group["Category"] == "Critical SIF Precursor").sum() if "Category" in group.columns else 0
            loc_stats[loc_name] = {
                "count": len(group),
                "avg_risk": round(avg_risk, 1),
                "critical_count": crit_count,
                "top_hazard": group["Incident_Type"].mode()[0] if "Incident_Type" in group.columns and not group["Incident_Type"].mode().empty else "General"
            }

    # Plot known facilities
    for loc_name, coords in OIL_INDIA_LOCATIONS.items():
        lat, lon = coords["lat"], coords["lon"]
        stats = loc_stats.get(loc_name, {"count": 1, "avg_risk": 45, "critical_count": 0, "top_hazard": "General"})
        
        avg_risk = stats["avg_risk"]
        count = stats["count"]
        
        # Determine color
        if avg_risk >= 75 or stats["critical_count"] > 0:
            color = "#ef4444"
            fill_color = "#dc2626"
            risk_tier = "CRITICAL RISK"
        elif avg_risk >= 50:
            color = "#f59e0b"
            fill_color = "#d97706"
            risk_tier = "ELEVATED RISK"
        else:
            color = "#22c55e"
            fill_color = "#16a34a"
            risk_tier = "ROUTINE"

        radius = max(8, min(24, 6 + count * 1.5))
        
        # Add to heatmap list
        heat_data.append([lat, lon, float(avg_risk / 10.0)])

        popup_html = f"""
        <div style="font-family: Arial, sans-serif; font-size:12px; width:220px;">
            <b style="font-size:14px; color:{color};">{loc_name}</b><br/>
            <b>Type:</b> {coords.get('type', 'Asset')}<br/>
            <b>State:</b> {coords.get('state', 'India')}<br/>
            <hr style="margin:4px 0; border: 0.5px solid #ccc;"/>
            <b>Total Reports:</b> {count}<br/>
            <b>Avg Risk Score:</b> {avg_risk}% ({risk_tier})<br/>
            <b>Critical SIF Incidents:</b> {stats['critical_count']}<br/>
            <b>Top Hazard:</b> {stats['top_hazard']}
        </div>
        """

        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{loc_name} ? Avg Risk: {avg_risk}%",
            color=color,
            fill=True,
            fill_color=fill_color,
            fill_opacity=0.75,
            weight=2
        ).add_to(m)

    # Add heatmap layer
    if heat_data:
        HeatMap(heat_data, radius=25, blur=18, min_opacity=0.4).add_to(m)

    # Render via streamlit_folium or html component
    try:
        from streamlit_folium import st_folium
        st_folium(m, width="100%", height=420, returned_objects=[])
    except Exception:
        import streamlit.components.v1 as components
        components.html(m._repr_html_(), height=430)
