from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Text, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import BaseModel

class SOSEvent(BaseModel):
    __tablename__ = "sos_events"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False, index=True)  # ACTIVE, RESOLVED, CANCELLED
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    address_note: Mapped[str] = mapped_column(String(255), nullable=True)
    trigger_type: Mapped[str] = mapped_column(String(50), default="MANUAL", nullable=False) # MANUAL, ONE_TOUCH
    emergency_notes: Mapped[str] = mapped_column(Text, nullable=True)
    
    resolved_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    resolution_notes: Mapped[str] = mapped_column(Text, nullable=True)
    resolved_by: Mapped[str] = mapped_column(String(50), nullable=True) # "USER" or "ADMIN"

    user = relationship("User", back_populates="sos_events")
    audit_entries = relationship("SOSAuditLog", back_populates="sos_event", cascade="all, delete-orphan", order_by="desc(SOSAuditLog.created_at)")

    @property
    def is_active(self) -> bool:
        return self.status == "ACTIVE"

    def __repr__(self):
        return f"<SOSEvent #{self.id} Status={self.status} User={self.user_id}>"

class SOSAuditLog(BaseModel):
    __tablename__ = "sos_audit_logs"

    sos_event_id: Mapped[int] = mapped_column(Integer, ForeignKey("sos_events.id", ondelete="CASCADE"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False) # ACTIVATED, RESOLVED, CANCELLED, LOCATION_UPDATED
    actor_email: Mapped[str] = mapped_column(String(120), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    sos_event = relationship("SOSEvent", back_populates="audit_entries")

    def __repr__(self):
        return f"<SOSAuditLog SOS={self.sos_event_id} Action={self.action}>"
