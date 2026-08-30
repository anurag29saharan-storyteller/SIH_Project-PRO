"""
Data access repository implementing CRUD, aggregation, and demo data seeding.
"""
import random
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from src.domain.models import Report, AnalysisResult, AuditLog
from src.domain.schemas import AnalysisResultSchema, ReportCreateSchema
from src.domain.constants import INCIDENT_TYPES, OIL_INDIA_LOCATIONS
from src.domain.rules import calculate_rule_based_sif


class ReportRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_report(
        self,
        narrative: str,
        location: str,
        analysis_data: AnalysisResultSchema,
        submitter_id: str = "field_officer",
        incident_date: Optional[datetime] = None
    ) -> Report:
        """Creates a new report record along with its associated analysis result."""
        if incident_date is None:
            incident_date = datetime.utcnow()

        report = Report(
            narrative=narrative.strip(),
            location=location,
            submitter_id=submitter_id,
            incident_date=incident_date,
            status="TRIAGED" if analysis_data.score < 80 else "CRITICAL_ESCALATED"
        )
        self.session.add(report)
        self.session.flush()

        analysis = AnalysisResult(
            report_id=report.id,
            category=analysis_data.category,
            score=analysis_data.score,
            matched_energy=analysis_data.matched_energy,
            matched_controls=analysis_data.matched_controls,
            corrective_actions=analysis_data.corrective_actions,
            engine_name=analysis_data.engine_name,
            used_fallback=analysis_data.used_fallback,
            fallback_reason=analysis_data.fallback_reason,
            confidence=analysis_data.confidence,
            prompt_tokens=analysis_data.prompt_tokens,
            completion_tokens=analysis_data.completion_tokens,
            cost_usd=analysis_data.cost_usd,
            latency_ms=analysis_data.latency_ms,
            created_at=datetime.utcnow()
        )
        self.session.add(analysis)
        self.session.commit()
        self.session.refresh(report)
        return report

    def get_recent_reports(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetches recent reports joined with their primary analysis results."""
        results = (
            self.session.query(Report, AnalysisResult)
            .join(AnalysisResult, Report.id == AnalysisResult.report_id)
            .order_by(desc(Report.incident_date))
            .limit(limit)
            .all()
        )
        data = []
        for rep, ana in results:
            data.append({
                "id": rep.id,
                "date": rep.incident_date.strftime("%Y-%m-%d %H:%M"),
                "location": rep.location,
                "narrative": rep.narrative,
                "category": ana.category,
                "score": ana.score,
                "matched_energy": ana.matched_energy,
                "matched_controls": ana.matched_controls,
                "corrective_actions": ana.corrective_actions,
                "engine": ana.engine_name,
                "used_fallback": ana.used_fallback,
                "status": rep.status,
                "cost_usd": ana.cost_usd,
                "latency_ms": ana.latency_ms
            })
        return data

    def get_all_reports_dataframe(self) -> pd.DataFrame:
        """Returns all reports as a flattened Pandas DataFrame for dashboard analytics."""
        results = (
            self.session.query(Report, AnalysisResult)
            .join(AnalysisResult, Report.id == AnalysisResult.report_id)
            .order_by(Report.incident_date.asc())
            .all()
        )
        if not results:
            return pd.DataFrame()

        rows = []
        for rep, ana in results:
            first_energy = ana.matched_energy[0] if ana.matched_energy else "General Safety"
            rows.append({
                "Report_ID": rep.id,
                "Date": rep.incident_date,
                "Location": rep.location,
                "Narrative": rep.narrative,
                "Risk_Score": ana.score,
                "Category": ana.category,
                "Incident_Type": first_energy,
                "Detected_Energy": ", ".join(ana.matched_energy) if ana.matched_energy else "None",
                "Control_Failures": ", ".join(ana.matched_controls) if ana.matched_controls else "None",
                "Engine": ana.engine_name,
                "Status": rep.status,
                "Cost_USD": ana.cost_usd
            })
        return pd.DataFrame(rows)

    def get_kpi_summary(self) -> Dict[str, Any]:
        """Aggregates high-level SIF KPIs."""
        total_reports = self.session.query(Report).count()
        if total_reports == 0:
            return {
                "total_reports": 0,
                "critical_count": 0,
                "critical_pct": 0.0,
                "avg_score": 0.0,
                "top_location": "N/A",
                "top_hazard": "N/A"
            }

        critical_count = (
            self.session.query(AnalysisResult)
            .filter(AnalysisResult.category == "Critical SIF Precursor")
            .count()
        )
        avg_score = self.session.query(func.avg(AnalysisResult.score)).scalar() or 0.0

        return {
            "total_reports": total_reports,
            "critical_count": critical_count,
            "critical_pct": (critical_count / total_reports) * 100.0,
            "avg_score": round(float(avg_score), 1)
        }

    def clear_all(self):
        """Truncates all reports and analysis results."""
        self.session.query(AnalysisResult).delete()
        self.session.query(Report).delete()
        self.session.commit()

    def seed_demo_data(self, count: int = 150):
        """Seeds realistic Oil & Gas near-miss reports into the persistent database."""
        sample_narratives = [
            ("Scaffold planks unfastened at 8m height without safety harness tie-off during paint touchup.", "Fall from Height"),
            ("Forklift reversing near loading bay without audible backup beeper or spotter present.", "Struck-By / Vehicle"),
            ("Cracked high-pressure steam valve whistling near boiler unit 2, no perimeter barricade.", "Pressure / Steam Systems"),
            ("Hydrocarbon gas smell near tank farm manifold, gas detector alarm had battery removed.", "Chemical / Gas Release"),
            ("Worker clearing jammed conveyor belt while motor running, emergency stop button bypassed.", "Caught-in / Machinery"),
            ("Crane load swung violently over worker gangway because tagline was not attached.", "Lifting / Crane Ops"),
            ("Electrician working on 415V MCC panel without LOTO permit or arc flash shield.", "Electrical"),
            ("Unattended hot work welding near diesel storage tank with dry chemical fire extinguisher missing.", "Fire / Explosion"),
            ("Personnel entered mud tank for cleaning without confined space permit or forced ventilation.", "Confined Space"),
            ("Excavation wall cracked after heavy rain, workers inside trench without trench box or shoring.", "Excavation / Trenching"),
            ("Loose handrail on offshore rigOI-2 catwalk above open sea, no life vest worn.", "Working Offshore / Marine Rig"),
            ("Routine housekeeping: discarded oily rags stored in open bin near workshop.", "Routine Safety Observation"),
            ("Trip hazard: air hose trailing across main walkway in compressor shed.", "Routine Safety Observation"),
            ("Safety sign faded and illegible near entrance gate 4.", "Routine Safety Observation"),
            ("Bina harness worker elevated platform par kaam kar raha tha, height safety violated.", "Fall from Height"),
            ("Gas leak chingari ke paas dekha gaya, aag lagne ka khatra tha.", "Fire / Explosion")
        ]

        locations = list(OIL_INDIA_LOCATIONS.keys())
        now = datetime.utcnow()

        for i in range(count):
            narrative, default_type = random.choice(sample_narratives)
            # Add minor variation
            variation = f" [Ref #{1000 + i}]"
            full_text = narrative + variation
            loc = random.choice(locations)
            days_ago = random.randint(0, 90)
            date = now - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))

            cat, score, matched_e, matched_c, actions = calculate_rule_based_sif(full_text)
            
            schema = AnalysisResultSchema(
                category=cat,
                score=score,
                matched_energy=matched_e,
                matched_controls=matched_c,
                corrective_actions=actions,
                engine_name="Local Engine (Seeded)",
                used_fallback=False,
                confidence=0.95,
                prompt_tokens=0,
                completion_tokens=0,
                cost_usd=0.0,
                latency_ms=1.2,
                text=full_text
            )
            self.create_report(full_text, loc, schema, submitter_id="sih_demo_seeder", incident_date=date)
