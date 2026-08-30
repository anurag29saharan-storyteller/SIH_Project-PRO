"""
SQLAlchemy ORM models for persistent database storage of SIF reports,
analysis results, and audit trails.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    narrative = Column(Text, nullable=False, index=True)
    location = Column(String(120), nullable=False, default="Duliajan Operational HQ", index=True)
    submitter_id = Column(String(80), nullable=False, default="operator")
    incident_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    status = Column(String(50), nullable=False, default="TRIAGED")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 1-to-1 or 1-to-many relationship with analysis results
    analysis_results = relationship("AnalysisResult", back_populates="report", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Report(id={self.id}, location='{self.location}', date='{self.incident_date}')>"


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    score = Column(Integer, nullable=False, index=True)
    matched_energy = Column(JSON, nullable=False, default=list)
    matched_controls = Column(JSON, nullable=False, default=list)
    corrective_actions = Column(JSON, nullable=False, default=list)
    engine_name = Column(String(60), nullable=False, default="Local Engine")
    used_fallback = Column(Boolean, nullable=False, default=False)
    fallback_reason = Column(String(255), nullable=True)
    confidence = Column(Float, nullable=False, default=1.0)
    prompt_tokens = Column(Integer, nullable=False, default=0)
    completion_tokens = Column(Integer, nullable=False, default=0)
    cost_usd = Column(Float, nullable=False, default=0.0)
    latency_ms = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    report = relationship("Report", back_populates="analysis_results")

    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, report_id={self.report_id}, category='{self.category}', score={self.score})>"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(80), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, user='{self.user_id}', action='{self.action}')>"
