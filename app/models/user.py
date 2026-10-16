from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import BaseModel

class Role(BaseModel):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    users = relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role {self.name}>"

class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=False)
    role = relationship("Role", back_populates="users", lazy="joined")

    emergency_contacts = relationship("EmergencyContact", back_populates="user", cascade="all, delete-orphan", order_by="EmergencyContact.priority_order")
    sos_events = relationship("SOSEvent", back_populates="user", cascade="all, delete-orphan", order_by="desc(SOSEvent.created_at)")
    incident_reports = relationship("IncidentReport", foreign_keys="[IncidentReport.user_id]", back_populates="user", cascade="all, delete-orphan", order_by="desc(IncidentReport.created_at)")
    checklist_progress = relationship("UserChecklistProgress", back_populates="user", cascade="all, delete-orphan")
    tip_views = relationship("TipView", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan", order_by="desc(Notification.created_at)")
    activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan", order_by="desc(UserActivity.created_at)")

    @property
    def is_admin(self) -> bool:
        return bool(self.role and self.role.name == "ADMIN")

    def to_safe_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "phone": self.phone or "",
            "city": self.city or "",
            "is_active": self.is_active,
            "role": self.role.name if self.role else "USER",
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<User {self.email}>"

class UserActivity(BaseModel):
    __tablename__ = "user_activities"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)

    user = relationship("User", back_populates="activities")

    def __repr__(self):
        return f"<UserActivity {self.user_id}: {self.action}>"
