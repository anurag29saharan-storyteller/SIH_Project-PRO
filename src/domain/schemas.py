"""
Pydantic data validation schemas for SIF Precursor Intelligence Engine.
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class SeverityCategory(str, Enum):
    CRITICAL = "Critical SIF Precursor"
    POTENTIAL = "Potential Precursor / Elevated Risk"
    ROUTINE = "Routine Safety Observation"


class AnalysisResultSchema(BaseModel):
    category: SeverityCategory
    score: int = Field(..., ge=0, le=100, description="SIF Risk Score from 0 to 100")
    matched_energy: List[str] = Field(default_factory=list)
    matched_controls: List[str] = Field(default_factory=list)
    corrective_actions: List[str] = Field(default_factory=list)
    engine_name: str = "Local Engine"
    used_fallback: bool = False
    fallback_reason: Optional[str] = None
    confidence: float = 1.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    text: str = ""

    class Config:
        use_enum_values = True


class ReportCreateSchema(BaseModel):
    narrative: str = Field(..., min_length=5, max_length=5000)
    location: str = "Duliajan Operational HQ"
    submitter_id: str = "field_officer"
    incident_date: Optional[datetime] = None


class ReportResponseSchema(BaseModel):
    id: int
    narrative: str
    location: str
    incident_date: datetime
    created_at: datetime
    submitter_id: str
    status: str
    analysis: Optional[AnalysisResultSchema] = None


class LLMStructuredOutput(BaseModel):
    category: SeverityCategory
    score: int = Field(..., ge=0, le=100)
    matched_high_energy_sources: List[str]
    matched_control_failures: List[str]
    root_cause_hypothesis: str
    recommended_corrective_actions: List[str]
    barrier_strength_rating: str = Field(description="Strong, Degraded, or Absent")


class SimilarReportSchema(BaseModel):
    report_id: int
    location: str
    category: str
    score: int
    snippet: str
    similarity_score: float


class ForecastPoint(BaseModel):
    date: str
    predicted_score: float
    lower_bound: float
    upper_bound: float
    is_anomaly: bool = False
