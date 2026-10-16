from typing import Optional, Tuple
from flask import session, request
from app.repositories.user_repo import UserRepository
from app.repositories.notification_repo import NotificationRepository
from app.repositories.audit_repo import AuditRepository
from app.security.hashing import hash_password, verify_password
from app.models.user import User

class AuthService:
    @staticmethod
    def register_user(data: dict, ip_address: str = "") -> Tuple[Optional[User], Optional[str]]:
        email = data["email"].strip().lower()
        if UserRepository.get_by_email(email):
            return None, "An account with this email already exists."

        user_role = UserRepository.get_role_by_name("USER")
        if not user_role:
            user_role = UserRepository.create_role("USER", "Standard Platform User")

        pwd_hash = hash_password(data["password"])
        user = UserRepository.create_user(
            email=email,
            password_hash=pwd_hash,
            full_name=data["full_name"],
            role_id=user_role.id,
            phone=data.get("phone", ""),
            city=data.get("city", "")
        )

        # Log audit & user activity
        AuditRepository.log(
            action="USER_REGISTERED",
            category="AUTH",
            user_id=user.id,
            user_email=user.email,
            details=f"New user registered with name: {user.full_name}",
            ip_address=ip_address
        )
        UserRepository.log_activity(
            user_id=user.id,
            action="Account Created",
            details="Registered for Women Safety Platform",
            ip_address=ip_address
        )

        # Send welcome notification
        NotificationRepository.create_notification(
            user_id=user.id,
            title="Welcome to Women Safety Platform",
            message="Your account is active. Start by adding trusted emergency contacts and reviewing the safety checklist.",
            notification_type="System",
            link_url="/checklist"
        )

        return user, None

    @staticmethod
    def authenticate_user(email: str, password: str, ip_address: str = "") -> Tuple[Optional[User], Optional[str]]:
        user = UserRepository.get_by_email(email)
        if not user:
            AuditRepository.log(
                action="LOGIN_FAILED",
                category="AUTH",
                user_email=email,
                details="Invalid email address attempted.",
                ip_address=ip_address
            )
            return None, "Invalid email or password."

        if not user.is_active:
            AuditRepository.log(
                action="LOGIN_BLOCKED",
                category="AUTH",
                user_id=user.id,
                user_email=user.email,
                details="Attempted login on deactivated account.",
                ip_address=ip_address
            )
            return None, "This account has been deactivated. Please contact support."

        if not verify_password(password, user.password_hash):
            AuditRepository.log(
                action="LOGIN_FAILED",
                category="AUTH",
                user_id=user.id,
                user_email=user.email,
                details="Incorrect password attempt.",
                ip_address=ip_address
            )
            return None, "Invalid email or password."

        # Successful login
        AuditRepository.log(
            action="LOGIN_SUCCESS",
            category="AUTH",
            user_id=user.id,
            user_email=user.email,
            details=f"User logged in ({user.role.name})",
            ip_address=ip_address
        )
        UserRepository.log_activity(
            user_id=user.id,
            action="Login",
            details="Successful login",
            ip_address=ip_address
        )

        return user, None

    @staticmethod
    def start_session(user: User):
        session.clear()
        session["user_id"] = user.id
        session["user_email"] = user.email
        session["user_name"] = user.full_name
        session["user_role"] = user.role.name if user.role else "USER"
        session.permanent = True

    @staticmethod
    def end_session(user_id: Optional[int] = None, ip_address: str = ""):
        if user_id:
            user = UserRepository.get_by_id(user_id)
            if user:
                AuditRepository.log(
                    action="LOGOUT",
                    category="AUTH",
                    user_id=user.id,
                    user_email=user.email,
                    details="User logged out",
                    ip_address=ip_address
                )
                UserRepository.log_activity(
                    user_id=user.id,
                    action="Logout",
                    details="Session ended",
                    ip_address=ip_address
                )
        session.clear()
