from typing import Optional, List, Tuple
from sqlalchemy import select, func, desc
from app.database import db_session
from app.models.notification import Notification
from app.models.user import User, Role

class NotificationRepository:
    @staticmethod
    def get_by_id(notification_id: int) -> Optional[Notification]:
        return db_session.get(Notification, notification_id)

    @staticmethod
    def create_notification(
        user_id: int,
        title: str,
        message: str,
        notification_type: str = "System",
        link_url: Optional[str] = None
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            title=title.strip(),
            message=message.strip(),
            notification_type=notification_type.strip(),
            link_url=link_url.strip() if link_url else None,
            is_read=False
        )
        db_session.add(notif)
        db_session.commit()
        db_session.refresh(notif)
        return notif

    @staticmethod
    def get_for_user(
        user_id: int,
        page: int = 1,
        per_page: int = 15,
        unread_only: bool = False
    ) -> Tuple[List[Notification], int]:
        stmt = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            stmt = stmt.where(Notification.is_read.is_(False))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db_session.execute(count_stmt).scalar() or 0

        notifications = list(db_session.execute(
            stmt.order_by(desc(Notification.created_at)).offset((page - 1) * per_page).limit(per_page)
        ).scalars().all())

        return notifications, total

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        stmt = select(func.count(Notification.id)).where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False)
        )
        return db_session.execute(stmt).scalar() or 0

    @staticmethod
    def mark_as_read(notification_id: int, user_id: int) -> bool:
        stmt = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id
        )
        notif = db_session.execute(stmt).scalars().first()
        if notif:
            notif.is_read = True
            db_session.commit()
            return True
        return False

    @staticmethod
    def mark_all_as_read(user_id: int) -> int:
        stmt = select(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False)
        )
        unread = list(db_session.execute(stmt).scalars().all())
        for n in unread:
            n.is_read = True
        db_session.commit()
        return len(unread)

    @staticmethod
    def notify_admins(title: str, message: str, notification_type: str = "System", link_url: Optional[str] = None):
        # Find all admin users
        stmt = select(User).join(Role).where(Role.name == "ADMIN", User.is_active.is_(True))
        admins = db_session.execute(stmt).scalars().all()
        for admin in admins:
            NotificationRepository.create_notification(
                user_id=admin.id,
                title=title,
                message=message,
                notification_type=notification_type,
                link_url=link_url
            )

    @staticmethod
    def get_metrics() -> dict:
        total = db_session.execute(select(func.count(Notification.id))).scalar() or 0
        unread = db_session.execute(
            select(func.count(Notification.id)).where(Notification.is_read.is_(False))
        ).scalar() or 0
        return {
            "total_notifications": total,
            "unread_notifications": unread
        }
