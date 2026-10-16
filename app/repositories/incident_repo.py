from typing import Optional, List, Tuple
from datetime import datetime, timezone
from sqlalchemy import select, func, desc, or_
from app.database import db_session
from app.models.incident import IncidentReport, IncidentTimeline
from app.models.user import User

class IncidentRepository:
    @staticmethod
    def get_by_id(incident_id: int) -> Optional[IncidentReport]:
        return db_session.get(IncidentReport, incident_id)

    @staticmethod
    def create_report(
        user_id: int,
        incident_type: str,
        incident_date: datetime,
        general_area: str,
        description: str,
        severity: str = "MEDIUM"
    ) -> IncidentReport:
        report = IncidentReport(
            user_id=user_id,
            incident_type=incident_type,
            incident_date=incident_date,
            general_area=general_area,
            description=description,
            severity=severity,
            status="SUBMITTED"
        )
        db_session.add(report)
        db_session.commit()
        db_session.refresh(report)

        # Add initial timeline
        timeline = IncidentTimeline(
            incident_id=report.id,
            actor_name="Report Author",
            actor_role="USER",
            action="REPORT_SUBMITTED",
            notes="Initial incident report submitted for review."
        )
        db_session.add(timeline)
        db_session.commit()

        return report

    @staticmethod
    def get_user_incidents(
        user_id: int,
        search: str = "",
        type_filter: str = "",
        severity_filter: str = "",
        status_filter: str = "",
        page: int = 1,
        per_page: int = 10
    ) -> Tuple[List[IncidentReport], int]:
        stmt = select(IncidentReport).where(IncidentReport.user_id == user_id)

        if search:
            s = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(IncidentReport.description).like(s),
                    func.lower(IncidentReport.general_area).like(s),
                    func.lower(IncidentReport.incident_type).like(s)
                )
            )

        if type_filter:
            stmt = stmt.where(IncidentReport.incident_type == type_filter)
        if severity_filter:
            stmt = stmt.where(IncidentReport.severity == severity_filter)
        if status_filter:
            stmt = stmt.where(IncidentReport.status == status_filter)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db_session.execute(count_stmt).scalar() or 0

        reports = list(db_session.execute(
            stmt.order_by(desc(IncidentReport.created_at)).offset((page - 1) * per_page).limit(per_page)
        ).scalars().all())

        return reports, total

    @staticmethod
    def list_all_incidents(
        search: str = "",
        type_filter: str = "",
        severity_filter: str = "",
        status_filter: str = "",
        page: int = 1,
        per_page: int = 15
    ) -> Tuple[List[IncidentReport], int]:
        stmt = select(IncidentReport).join(User, IncidentReport.user_id == User.id)

        if search:
            s = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(User.full_name).like(s),
                    func.lower(User.email).like(s),
                    func.lower(IncidentReport.description).like(s),
                    func.lower(IncidentReport.general_area).like(s),
                    func.lower(IncidentReport.incident_type).like(s)
                )
            )

        if type_filter:
            stmt = stmt.where(IncidentReport.incident_type == type_filter)
        if severity_filter:
            stmt = stmt.where(IncidentReport.severity == severity_filter)
        if status_filter:
            stmt = stmt.where(IncidentReport.status == status_filter)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db_session.execute(count_stmt).scalar() or 0

        reports = list(db_session.execute(
            stmt.order_by(desc(IncidentReport.created_at)).offset((page - 1) * per_page).limit(per_page)
        ).scalars().all())

        return reports, total

    @staticmethod
    def update_status(
        incident: IncidentReport,
        status: str,
        admin_id: Optional[int] = None,
        resolution_notes: str = ""
    ) -> IncidentReport:
        incident.status = status
        if resolution_notes:
            incident.resolution_notes = resolution_notes
        if status in ("RESOLVED", "CLOSED"):
            incident.resolved_at = datetime.now(timezone.utc)
            incident.resolved_by_admin_id = admin_id
        db_session.commit()
        db_session.refresh(incident)
        return incident

    @staticmethod
    def add_timeline_entry(
        incident_id: int,
        actor_name: str,
        actor_role: str,
        action: str,
        notes: str = ""
    ) -> IncidentTimeline:
        entry = IncidentTimeline(
            incident_id=incident_id,
            actor_name=actor_name,
            actor_role=actor_role,
            action=action,
            notes=notes
        )
        db_session.add(entry)
        db_session.commit()
        return entry

    @staticmethod
    def get_metrics() -> dict:
        total = db_session.execute(select(func.count(IncidentReport.id))).scalar() or 0
        pending = db_session.execute(
            select(func.count(IncidentReport.id)).where(IncidentReport.status.in_(["SUBMITTED", "UNDER REVIEW"]))
        ).scalar() or 0
        resolved = db_session.execute(
            select(func.count(IncidentReport.id)).where(IncidentReport.status.in_(["RESOLVED", "CLOSED"]))
        ).scalar() or 0

        return {
            "total_incidents": total,
            "pending_incidents": pending,
            "resolved_incidents": resolved
        }
