from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import BaseModel

class ChecklistItem(BaseModel):
    __tablename__ = "checklist_items"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(60), default="General", nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    user_progress = relationship("UserChecklistProgress", back_populates="item", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChecklistItem {self.title}>"

class UserChecklistProgress(BaseModel):
    __tablename__ = "user_checklist_progress"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("checklist_items.id", ondelete="CASCADE"), nullable=False, index=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    user = relationship("User", back_populates="checklist_progress")
    item = relationship("ChecklistItem", back_populates="user_progress")

    def __repr__(self):
        return f"<UserChecklistProgress User={self.user_id} Item={self.item_id} Completed={self.is_completed}>"
