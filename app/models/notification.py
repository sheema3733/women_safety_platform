from sqlalchemy import String, Boolean, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import BaseModel

class Notification(BaseModel):
    __tablename__ = "notifications"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    notification_type: Mapped[str] = mapped_column(String(50), default="System", nullable=False, index=True) 
    # SOS Created, SOS Resolved, SOS Cancelled, Incident Submitted, Incident Status Changed, New Safety Tip, Checklist Reminder, System
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    link_url: Mapped[str] = mapped_column(String(255), nullable=True)

    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification User={self.user_id} Type={self.notification_type} Read={self.is_read}>"
