from typing import Dict, Any, List
from sqlalchemy import select, func, desc
from app.database import db_session
from app.models.user import User
from app.models.sos import SOSEvent
from app.models.incident import IncidentReport
from app.models.resource import EmergencyResource
from app.models.tip import SafetyTip, TipView
from app.models.checklist import ChecklistItem, UserChecklistProgress
from app.models.notification import Notification

class AnalyticsService:
    @staticmethod
    def get_dashboard_kpis() -> Dict[str, Any]:
        """Aggregate key platform performance indicators."""
        total_users = db_session.execute(select(func.count(User.id))).scalar() or 0
        active_users = db_session.execute(select(func.count(User.id)).where(User.is_active.is_(True))).scalar() or 0
        
        total_sos = db_session.execute(select(func.count(SOSEvent.id))).scalar() or 0
        active_sos = db_session.execute(select(func.count(SOSEvent.id)).where(SOSEvent.status == "ACTIVE")).scalar() or 0
        resolved_sos = db_session.execute(select(func.count(SOSEvent.id)).where(SOSEvent.status == "RESOLVED")).scalar() or 0
        cancelled_sos = db_session.execute(select(func.count(SOSEvent.id)).where(SOSEvent.status == "CANCELLED")).scalar() or 0

        total_incidents = db_session.execute(select(func.count(IncidentReport.id))).scalar() or 0
        pending_incidents = db_session.execute(
            select(func.count(IncidentReport.id)).where(IncidentReport.status.in_(["SUBMITTED", "UNDER REVIEW"]))
        ).scalar() or 0
        resolved_incidents = db_session.execute(
            select(func.count(IncidentReport.id)).where(IncidentReport.status.in_(["RESOLVED", "CLOSED"]))
        ).scalar() or 0

        total_resources = db_session.execute(select(func.count(EmergencyResource.id))).scalar() or 0
        total_tips = db_session.execute(select(func.count(SafetyTip.id))).scalar() or 0
        total_views = db_session.execute(select(func.sum(SafetyTip.view_count))).scalar() or 0
        unread_notifications = db_session.execute(select(func.count(Notification.id)).where(Notification.is_read.is_(False))).scalar() or 0

        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_sos": total_sos,
            "active_sos": active_sos,
            "resolved_sos": resolved_sos,
            "cancelled_sos": cancelled_sos,
            "total_incidents": total_incidents,
            "pending_incidents": pending_incidents,
            "resolved_incidents": resolved_incidents,
            "total_resources": total_resources,
            "total_tips": total_tips,
            "total_views": total_views,
            "unread_notifications": unread_notifications
        }

    @staticmethod
    def get_charts_data() -> Dict[str, Any]:
        """Aggregate structured chart datasets using Warm Plum + Forest Mint color palette."""
        # Palette definition:
        # Plum: #734B6D, Mint: #4A8B71, Coral: #C77366, Gray-Purple: #A2829D, Dark Plum: #231A22
        
        # 1. SOS Status Breakdown
        sos_statuses = db_session.execute(
            select(SOSEvent.status, func.count(SOSEvent.id)).group_by(SOSEvent.status)
        ).all()
        sos_status_dict = {s: c for s, c in sos_statuses}
        sos_status_chart = {
            "labels": ["ACTIVE", "RESOLVED", "CANCELLED"],
            "data": [
                sos_status_dict.get("ACTIVE", 0),
                sos_status_dict.get("RESOLVED", 0),
                sos_status_dict.get("CANCELLED", 0)
            ],
            "colors": ["#C77366", "#4A8B71", "#A2829D"]
        }

        # 2. Incident Categories Breakdown
        incident_cats = db_session.execute(
            select(IncidentReport.incident_type, func.count(IncidentReport.id)).group_by(IncidentReport.incident_type)
        ).all()
        inc_labels = [row[0] for row in incident_cats] if incident_cats else ["None Reported"]
        inc_counts = [row[1] for row in incident_cats] if incident_cats else [0]
        cat_palette = ["#734B6D", "#4A8B71", "#C77366", "#A2829D", "#3B5A80", "#E09F67"]
        incident_cat_chart = {
            "labels": inc_labels,
            "data": inc_counts,
            "colors": cat_palette[:len(inc_labels)]
        }

        # 3. Incident Severity Distribution
        sev_counts = db_session.execute(
            select(IncidentReport.severity, func.count(IncidentReport.id)).group_by(IncidentReport.severity)
        ).all()
        sev_dict = {s: c for s, c in sev_counts}
        incident_sev_chart = {
            "labels": ["LOW", "MEDIUM", "HIGH"],
            "data": [
                sev_dict.get("LOW", 0),
                sev_dict.get("MEDIUM", 0),
                sev_dict.get("HIGH", 0)
            ],
            "colors": ["#4A8B71", "#A2829D", "#C77366"]
        }

        # 4. Emergency Resources by Category
        res_cats = db_session.execute(
            select(EmergencyResource.category, func.count(EmergencyResource.id)).group_by(EmergencyResource.category)
        ).all()
        res_labels = [row[0] for row in res_cats] if res_cats else ["No Resources"]
        res_counts = [row[1] for row in res_cats] if res_cats else [0]
        resource_cat_chart = {
            "labels": res_labels,
            "data": res_counts,
            "colors": ["#734B6D", "#4A8B71", "#C77366", "#A2829D", "#3B5A80"][:len(res_labels)]
        }

        # 5. Safety Tips by Category
        tip_cats = db_session.execute(
            select(SafetyTip.category, func.count(SafetyTip.id)).group_by(SafetyTip.category)
        ).all()
        tip_labels = [row[0] for row in tip_cats] if tip_cats else ["No Tips"]
        tip_counts = [row[1] for row in tip_cats] if tip_cats else [0]
        tip_cat_chart = {
            "labels": tip_labels,
            "data": tip_counts,
            "colors": ["#734B6D", "#4A8B71", "#A2829D", "#C77366", "#5C768D", "#8E6C88"][:len(tip_labels)]
        }

        # 6. Checklist Completion Rate
        total_items = db_session.execute(select(func.count(ChecklistItem.id))).scalar() or 0
        total_completions = db_session.execute(
            select(func.count(UserChecklistProgress.id)).where(UserChecklistProgress.is_completed.is_(True))
        ).scalar() or 0

        return {
            "sos_status": sos_status_chart,
            "incident_category": incident_cat_chart,
            "incident_severity": incident_sev_chart,
            "resource_category": resource_cat_chart,
            "tip_category": tip_cat_chart,
            "checklist": {
                "total_items": total_items,
                "total_completions": total_completions
            }
        }
