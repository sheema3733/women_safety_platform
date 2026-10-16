from typing import Optional, List, Tuple
from sqlalchemy import select, func, or_, desc
from app.database import db_session
from app.models.user import User, Role, UserActivity

class UserRepository:
    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        return db_session.get(User, user_id)

    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        stmt = select(User).where(func.lower(User.email) == func.lower(email.strip()))
        return db_session.execute(stmt).scalars().first()

    @staticmethod
    def get_role_by_name(name: str) -> Optional[Role]:
        stmt = select(Role).where(Role.name == name)
        return db_session.execute(stmt).scalars().first()

    @staticmethod
    def create_role(name: str, description: str = "") -> Role:
        role = Role(name=name, description=description)
        db_session.add(role)
        db_session.commit()
        return role

    @staticmethod
    def create_user(email: str, password_hash: str, full_name: str, role_id: int, phone: str = "", city: str = "") -> User:
        user = User(
            email=email.strip().lower(),
            password_hash=password_hash,
            full_name=full_name.strip(),
            role_id=role_id,
            phone=phone.strip(),
            city=city.strip(),
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @staticmethod
    def update_user(user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        db_session.commit()
        db_session.refresh(user)
        return user

    @staticmethod
    def list_users(
        search: str = "",
        role_filter: str = "",
        status_filter: str = "",
        page: int = 1,
        per_page: int = 15
    ) -> Tuple[List[User], int]:
        stmt = select(User).join(Role)

        if search:
            s = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(User.full_name).like(s),
                    func.lower(User.email).like(s),
                    func.lower(User.city).like(s)
                )
            )

        if role_filter:
            stmt = stmt.where(Role.name == role_filter)

        if status_filter == "active":
            stmt = stmt.where(User.is_active.is_(True))
        elif status_filter == "inactive":
            stmt = stmt.where(User.is_active.is_(False))

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db_session.execute(count_stmt).scalar() or 0

        # Paginate
        stmt = stmt.order_by(desc(User.created_at)).offset((page - 1) * per_page).limit(per_page)
        users = list(db_session.execute(stmt).scalars().all())

        return users, total

    @staticmethod
    def log_activity(user_id: int, action: str, details: str = "", ip_address: str = "") -> UserActivity:
        activity = UserActivity(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address
        )
        db_session.add(activity)
        db_session.commit()
        return activity

    @staticmethod
    def get_user_activities(user_id: int, limit: int = 20) -> List[UserActivity]:
        stmt = select(UserActivity).where(UserActivity.user_id == user_id).order_by(desc(UserActivity.created_at)).limit(limit)
        return list(db_session.execute(stmt).scalars().all())

    @staticmethod
    def get_metrics() -> dict:
        total_users = db_session.execute(select(func.count(User.id))).scalar() or 0
        active_users = db_session.execute(select(func.count(User.id)).where(User.is_active.is_(True))).scalar() or 0
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users
        }
