from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship as sa_relationship
from app.database.base import BaseModel

class EmergencyContact(BaseModel):
    __tablename__ = "emergency_contacts"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    relationship: Mapped[str] = mapped_column(String(60), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    is_trusted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    priority_order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    user = sa_relationship("User", back_populates="emergency_contacts")

    def __repr__(self):
        return f"<EmergencyContact {self.name} ({self.relationship})>"
