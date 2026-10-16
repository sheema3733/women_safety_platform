from typing import Optional, List, Tuple
from sqlalchemy import select, func, desc, or_
from app.database import db_session
from app.models.audit import AuditLog

class AuditRepository:
    @staticmethod
    def log(
        action: str,
        category: str,
        user_id: Optional[int] = None,
        user_email: Optional[str] = None,
        details: str = "",
        ip_address: str = ""
    ) -> AuditLog:
        # Sanitize details to ensure no password/secrets logged
        log = AuditLog(
            action=action.strip(),
            category=category.strip(),
            user_id=user_id,
            user_email=user_email.strip().lower() if user_email else None,
            details=details.strip() if details else None,
            ip_address=ip_address.strip() if ip_address else None
        )
        db_session.add(log)
        db_session.commit()
        return log

    @staticmethod
    def list_logs(
        search: str = "",
        category: str = "",
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[AuditLog], int]:
        stmt = select(AuditLog)

        if search:
            s = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(AuditLog.action).like(s),
                    func.lower(AuditLog.user_email).like(s),
                    func.lower(AuditLog.details).like(s)
                )
            )

        if category:
            stmt = stmt.where(AuditLog.category == category)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db_session.execute(count_stmt).scalar() or 0

        logs = list(db_session.execute(
            stmt.order_by(desc(AuditLog.created_at)).offset((page - 1) * per_page).limit(per_page)
        ).scalars().all())

        return logs, total

    @staticmethod
    def get_categories() -> List[str]:
        stmt = select(AuditLog.category).distinct().order_by(AuditLog.category)
        return [c for c in db_session.execute(stmt).scalars().all() if c]
