from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import BaseModel

class SafetyTip(BaseModel):
    __tablename__ = "safety_tips"

    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    summary: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    read_time_minutes: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    views = relationship("TipView", back_populates="tip", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SafetyTip {self.title} ({self.category})>"

class TipView(BaseModel):
    __tablename__ = "tip_views"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    tip_id: Mapped[int] = mapped_column(Integer, ForeignKey("safety_tips.id", ondelete="CASCADE"), nullable=False, index=True)
    viewed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="tip_views")
    tip = relationship("SafetyTip", back_populates="views")

    def __repr__(self):
        return f"<TipView User={self.user_id} Tip={self.tip_id}>"
