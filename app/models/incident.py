from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import BaseModel

class IncidentReport(BaseModel):
    __tablename__ = "incident_reports"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    incident_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    incident_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    general_area: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False, index=True) # LOW, MEDIUM, HIGH
    status: Mapped[str] = mapped_column(String(30), default="SUBMITTED", nullable=False, index=True) # SUBMITTED, UNDER REVIEW, RESOLVED, CLOSED
    
    resolution_notes: Mapped[str] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    resolved_by_admin_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    user = relationship("User", foreign_keys=[user_id], back_populates="incident_reports")
    resolved_by_admin = relationship("User", foreign_keys=[resolved_by_admin_id])
    timeline = relationship("IncidentTimeline", back_populates="incident", cascade="all, delete-orphan", order_by="IncidentTimeline.created_at")

    def __repr__(self):
        return f"<IncidentReport #{self.id} Type={self.incident_type} Severity={self.severity} Status={self.status}>"

class IncidentTimeline(BaseModel):
    __tablename__ = "incident_timelines"

    incident_id: Mapped[int] = mapped_column(Integer, ForeignKey("incident_reports.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_name: Mapped[str] = mapped_column(String(100), nullable=False)
    actor_role: Mapped[str] = mapped_column(String(20), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    incident = relationship("IncidentReport", back_populates="timeline")

    def __repr__(self):
        return f"<IncidentTimeline Incident={self.incident_id} Action={self.action}>"
