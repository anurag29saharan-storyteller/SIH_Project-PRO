"""
Enterprise PDF Exporter for SIF Incident Assessments and Dashboard Summaries
using ReportLab. Generates publication-grade executive safety documents.
"""
import io
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


def _create_styles():
    styles = getSampleStyleSheet()
    
    navy = colors.HexColor("#0f172a")
    dark_gray = colors.HexColor("#334155")
    
    styles.add(ParagraphStyle(
        "ReportTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=navy,
        alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=10,
        leading=14,
        textColor=dark_gray,
        alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        "SectionHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=navy,
        spaceBefore=10,
        spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=dark_gray
    ))
    styles.add(ParagraphStyle(
        "SeverityBadge",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        alignment=TA_CENTER,
        textColor=colors.white
    ))
    return styles


def generate_incident_pdf(
    report_text: str,
    analysis: Dict[str, Any],
    location: str = "Duliajan Operational HQ",
    report_id: Optional[int] = None
) -> bytes:
    """Generates a formal single-incident SIF precursor investigation document."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    styles = _create_styles()
    story = []

    category = analysis.get("category", "Potential Precursor / Elevated Risk")
    score = analysis.get("score", 0)
    matched_energy = analysis.get("matched_energy", [])
    matched_controls = analysis.get("matched_controls", [])
    corrective_actions = analysis.get("corrective_actions", [])
    engine_name = analysis.get("engine_name", "Local Rule Engine")

    # Determine badge color
    if score >= 80 or "Critical" in category:
        badge_bg = colors.HexColor("#dc2626")
        risk_label = "CRITICAL SIF PRECURSOR - IMMEDIATE ESCALATION"
    elif score >= 50:
        badge_bg = colors.HexColor("#d97706")
        risk_label = "POTENTIAL SIF PRECURSOR - ELEVATED RISK"
    else:
        badge_bg = colors.HexColor("#16a34a")
        risk_label = "ROUTINE SAFETY OBSERVATION - LOW SEVERITY"

    # Header
    story.append(Paragraph("OIL INDIA LIMITED ? HSE AUDIT & INVESTIGATION", styles["ReportSubtitle"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("SIF PRECURSOR ASSESSMENT REPORT", styles["ReportTitle"]))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%d-%b-%Y %H:%M:%S')} UTC | Engine: {engine_name}", styles["ReportSubtitle"]))
    story.append(Spacer(1, 10))

    # Severity Banner
    badge_data = [[Paragraph(f"<b>{risk_label} ? RISK SCORE: {score}/100</b>", styles["SeverityBadge"])]]
    badge_table = Table(badge_data, colWidths=[540])
    badge_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), badge_bg),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(badge_table)
    story.append(Spacer(1, 12))

    # Metadata Grid
    rid_str = f"SIF-OIL-{(report_id or 9942):05d}"
    meta_data = [
        [
            Paragraph("<b>Facility / Location:</b>", styles["BodyTextCustom"]),
            Paragraph(location, styles["BodyTextCustom"]),
            Paragraph("<b>Report Ref ID:</b>", styles["BodyTextCustom"]),
            Paragraph(rid_str, styles["BodyTextCustom"])
        ],
        [
            Paragraph("<b>Classification:</b>", styles["BodyTextCustom"]),
            Paragraph(category, styles["BodyTextCustom"]),
            Paragraph("<b>Direct Barrier State:</b>", styles["BodyTextCustom"]),
            Paragraph("FAILED / BYPASSED" if matched_controls else "DEGRADED / INTACT", styles["BodyTextCustom"])
        ]
    ]
    meta_table = Table(meta_data, colWidths=[120, 160, 120, 140])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # Narrative Section
    story.append(Paragraph("1. Incident / Observation Narrative", styles["SectionHeader"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceBefore=2, spaceAfter=6))
    story.append(Paragraph(f'<i>"{report_text}"</i>', styles["BodyTextCustom"]))
    story.append(Spacer(1, 10))

    # Factors Table
    story.append(Paragraph("2. Campbell Institute SIF Barrier & Energy Breakdown", styles["SectionHeader"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceBefore=2, spaceAfter=6))
    
    energy_str = "<br/>".join([f"? {e}" for e in matched_energy]) if matched_energy else "<i>None detected</i>"
    controls_str = "<br/>".join([f"? {c}" for c in matched_controls]) if matched_controls else "<i>None detected</i>"

    factors_data = [
        [
            Paragraph("<b>? High-Energy Sources Present</b>", styles["BodyTextCustom"]),
            Paragraph("<b>?? Direct Control / Barrier Failures</b>", styles["BodyTextCustom"])
        ],
        [
            Paragraph(energy_str, styles["BodyTextCustom"]),
            Paragraph(controls_str, styles["BodyTextCustom"])
        ]
    ]
    factors_table = Table(factors_data, colWidths=[270, 270])
    factors_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(factors_table)
    story.append(Spacer(1, 12))

    # Corrective Actions
    story.append(Paragraph("3. Recommended Hierarchy of Controls & Corrective Mitigations", styles["SectionHeader"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceBefore=2, spaceAfter=6))
    
    action_items = [[Paragraph(f"<b>[{i+1}]</b> {act}", styles["BodyTextCustom"])] for i, act in enumerate(corrective_actions)]
    if not action_items:
        action_items = [[Paragraph("Standard toolbox talk review and observation close-out.", styles["BodyTextCustom"])]]
    
    actions_table = Table(action_items, colWidths=[540])
    actions_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(actions_table)
    story.append(Spacer(1, 14))

    # Emergency Escalations
    story.append(Paragraph("4. Emergency Contact & Verification Sign-Off", styles["SectionHeader"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceBefore=2, spaceAfter=6))
    
    signoff_data = [
        [
            Paragraph("<b>National Emergency:</b> 112", styles["BodyTextCustom"]),
            Paragraph("<b>Gas Leak Cell:</b> 1906", styles["BodyTextCustom"]),
            Paragraph("<b>Duliajan HSE:</b> +91-374-2800555", styles["BodyTextCustom"])
        ],
        [
            Paragraph("<b>Safety Officer Signature:</b> ___________________", styles["BodyTextCustom"]),
            Paragraph("<b>Date:</b> ____________", styles["BodyTextCustom"]),
            Paragraph("<b>Status:</b> [  ] OPEN  [  ] CLOSED", styles["BodyTextCustom"])
        ]
    ]
    signoff_table = Table(signoff_data, colWidths=[180, 180, 180])
    signoff_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(signoff_table)

    doc.build(story)
    return buffer.getvalue()


def generate_batch_summary_pdf(df: pd.DataFrame) -> bytes:
    """Generates an executive batch summary PDF for multiple analyzed reports."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    styles = _create_styles()
    story = []

    total_count = len(df)
    critical_count = len(df[df["Category"] == "Critical SIF Precursor"]) if "Category" in df.columns else 0
    avg_score = df["Risk_Score"].mean() if "Risk_Score" in df.columns else 0

    # Header
    story.append(Paragraph("OIL INDIA LIMITED ? HSE INTELLIGENCE DIVISION", styles["ReportSubtitle"]))
    story.append(Paragraph("EXECUTIVE SIF BATCH AUDIT SUMMARY", styles["ReportTitle"]))
    story.append(Paragraph(f"Total Records Analyzed: {total_count} | Report Date: {datetime.now().strftime('%d-%b-%Y')}", styles["ReportSubtitle"]))
    story.append(Spacer(1, 12))

    # Metric summary box
    kpi_data = [
        [
            Paragraph("<b>Total Reports</b>", styles["BodyTextCustom"]),
            Paragraph("<b>Critical SIF Precursors</b>", styles["BodyTextCustom"]),
            Paragraph("<b>Critical Rate</b>", styles["BodyTextCustom"]),
            Paragraph("<b>Avg Risk Score</b>", styles["BodyTextCustom"])
        ],
        [
            Paragraph(f"<b>{total_count}</b>", styles["SectionHeader"]),
            Paragraph(f"<b><font color='#dc2626'>{critical_count}</font></b>", styles["SectionHeader"]),
            Paragraph(f"<b>{(critical_count/total_count*100):.1f}%</b>" if total_count > 0 else "0%", styles["SectionHeader"]),
            Paragraph(f"<b>{avg_score:.1f}%</b>", styles["SectionHeader"])
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[135, 135, 135, 135])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 14))

    # Top 10 Critical Incidents Table
    story.append(Paragraph("Top Critical Precursors Requiring Action", styles["SectionHeader"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceBefore=2, spaceAfter=6))

    top_df = df.sort_values(by="Risk_Score", ascending=False).head(12) if "Risk_Score" in df.columns else df.head(12)
    table_rows = [
        [
            Paragraph("<b>ID / Date</b>", styles["BodyTextCustom"]),
            Paragraph("<b>Location</b>", styles["BodyTextCustom"]),
            Paragraph("<b>Score</b>", styles["BodyTextCustom"]),
            Paragraph("<b>Hazard Category</b>", styles["BodyTextCustom"]),
            Paragraph("<b>Snippet</b>", styles["BodyTextCustom"])
        ]
    ]

    for _, r in top_df.iterrows():
        narr = str(r.get("Narrative", ""))[:65] + "..." if len(str(r.get("Narrative", ""))) > 65 else str(r.get("Narrative", ""))
        date_str = str(r.get("Date", ""))[:10]
        table_rows.append([
            Paragraph(date_str, styles["BodyTextCustom"]),
            Paragraph(str(r.get("Location", "Field")), styles["BodyTextCustom"]),
            Paragraph(f"<b>{int(r.get('Risk_Score', 0))}%</b>", styles["BodyTextCustom"]),
            Paragraph(str(r.get("Incident_Type", "General")), styles["BodyTextCustom"]),
            Paragraph(narr, styles["BodyTextCustom"])
        ])

    table_widget = Table(table_rows, colWidths=[65, 95, 45, 115, 220])
    table_widget.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(table_widget)

    doc.build(story)
    return buffer.getvalue()
