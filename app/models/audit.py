from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import BaseModel

class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    user_email: Mapped[str] = mapped_column(String(120), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True) # e.g. AUTH_LOGIN, SOS_ACTIVATED, USER_ACTIVATED
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # AUTH, SOS, INCIDENT, USER_MGMT, RESOURCE, SAFETY_TIP, SETTINGS
    details: Mapped[str] = mapped_column(Text, nullable=True) # Never passwords
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)

    user = relationship("User")

    def __repr__(self):
        return f"<AuditLog Action={self.action} Category={self.category} User={self.user_email}>"
