from typing import Optional, List, Tuple
from datetime import datetime, timezone
from sqlalchemy import select, func, desc, or_
from app.database import db_session
from app.models.sos import SOSEvent, SOSAuditLog
from app.models.user import User

class SOSRepository:
    @staticmethod
    def get_by_id(sos_id: int) -> Optional[SOSEvent]:
        return db_session.get(SOSEvent, sos_id)

    @staticmethod
    def get_active_for_user(user_id: int) -> Optional[SOSEvent]:
        stmt = (
            select(SOSEvent)
            .where(SOSEvent.user_id == user_id, SOSEvent.status == "ACTIVE")
            .order_by(desc(SOSEvent.created_at))
        )
        return db_session.execute(stmt).scalars().first()

    @staticmethod
    def create_event(
        user_id: int,
        trigger_type: str = "MANUAL",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        address_note: str = "",
        emergency_notes: str = ""
    ) -> SOSEvent:
        event = SOSEvent(
            user_id=user_id,
            status="ACTIVE",
            trigger_type=trigger_type,
            latitude=latitude,
            longitude=longitude,
            address_note=address_note,
            emergency_notes=emergency_notes
        )
        db_session.add(event)
        db_session.commit()
        db_session.refresh(event)
        return event

    @staticmethod
    def update_status(
        sos: SOSEvent,
        status: str,
        resolved_by: str = "USER",
        resolution_notes: str = ""
    ) -> SOSEvent:
        sos.status = status
        sos.resolved_by = resolved_by
        sos.resolution_notes = resolution_notes
        sos.resolved_at = datetime.now(timezone.utc)
        db_session.commit()
        db_session.refresh(sos)
        return sos

    @staticmethod
    def add_audit_log(sos_id: int, action: str, actor_email: str, notes: str = "") -> SOSAuditLog:
        log = SOSAuditLog(
            sos_event_id=sos_id,
            action=action,
            actor_email=actor_email,
            notes=notes
        )
        db_session.add(log)
        db_session.commit()
        return log

    @staticmethod
    def get_user_history(user_id: int, page: int = 1, per_page: int = 10) -> Tuple[List[SOSEvent], int]:
        stmt = select(SOSEvent).where(SOSEvent.user_id == user_id).order_by(desc(SOSEvent.created_at))
        
        count_stmt = select(func.count(SOSEvent.id)).where(SOSEvent.user_id == user_id)
        total = db_session.execute(count_stmt).scalar() or 0

        events = list(db_session.execute(stmt.offset((page - 1) * per_page).limit(per_page)).scalars().all())
        return events, total

    @staticmethod
    def list_all_sos(
        search: str = "",
        status_filter: str = "",
        page: int = 1,
        per_page: int = 15
    ) -> Tuple[List[SOSEvent], int]:
        stmt = select(SOSEvent).join(User)

        if search:
            s = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(User.full_name).like(s),
                    func.lower(User.email).like(s),
                    func.lower(SOSEvent.address_note).like(s)
                )
            )

        if status_filter:
            stmt = stmt.where(SOSEvent.status == status_filter.upper())

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db_session.execute(count_stmt).scalar() or 0

        events = list(db_session.execute(
            stmt.order_by(desc(SOSEvent.created_at)).offset((page - 1) * per_page).limit(per_page)
        ).scalars().all())

        return events, total

    @staticmethod
    def get_metrics() -> dict:
        total = db_session.execute(select(func.count(SOSEvent.id))).scalar() or 0
        active = db_session.execute(select(func.count(SOSEvent.id)).where(SOSEvent.status == "ACTIVE")).scalar() or 0
        resolved = db_session.execute(select(func.count(SOSEvent.id)).where(SOSEvent.status == "RESOLVED")).scalar() or 0
        cancelled = db_session.execute(select(func.count(SOSEvent.id)).where(SOSEvent.status == "CANCELLED")).scalar() or 0

        return {
            "total_sos": total,
            "active_sos": active,
            "resolved_sos": resolved,
            "cancelled_sos": cancelled
        }
