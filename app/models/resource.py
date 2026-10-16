from sqlalchemy import String, Boolean, Float, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import BaseModel

class EmergencyResource(BaseModel):
    __tablename__ = "emergency_resources"

    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(60), nullable=False, index=True) # Police Station, Hospital, Women’s Support Center, Safe Place, Emergency Support Center
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    general_area: Mapped[str] = mapped_column(String(150), nullable=False)
    demo_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    def __repr__(self):
        return f"<EmergencyResource {self.name} ({self.category} - {self.city})>"
