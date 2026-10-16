from typing import Optional
from app.repositories.incident_repo import IncidentRepository
from app.repositories.user_repo import UserRepository
from app.repositories.notification_repo import NotificationRepository
from app.repositories.audit_repo import AuditRepository
from app.models.incident import IncidentReport

class IncidentService:
    @staticmethod
    def submit_report(user_id: int, validated_data: dict, ip_address: str = "") -> IncidentReport:
        user = UserRepository.get_by_id(user_id)
        user_email = user.email if user else f"user_{user_id}"

        report = IncidentRepository.create_report(
            user_id=user_id,
            incident_type=validated_data["incident_type"],
            incident_date=validated_data["incident_date"],
            general_area=validated_data["general_area"],
            description=validated_data["description"],
            severity=validated_data["severity"]
        )

        AuditRepository.log(
            action="INCIDENT_SUBMITTED",
            category="INCIDENT",
            user_id=user_id,
            user_email=user_email,
            details=f"Report #{report.id} ({report.incident_type}) in {report.general_area}. Severity: {report.severity}",
            ip_address=ip_address
        )

        UserRepository.log_activity(
            user_id=user_id,
            action="Incident Reported",
            details=f"Submitted report #{report.id} ({report.incident_type})",
            ip_address=ip_address
        )

        # Notify user
        NotificationRepository.create_notification(
            user_id=user_id,
            title="Incident Report Received",
            message=f"Your report #{report.id} ({report.incident_type}) has been securely logged. Status: SUBMITTED.",
            notification_type="Incident Submitted",
            link_url=f"/incidents/{report.id}"
        )

        # Notify admin
        NotificationRepository.notify_admins(
            title=f"New Incident Report #{report.id} Submitted",
            message=f"Incident type '{report.incident_type}' ({report.severity} severity) reported in {report.general_area}.",
            notification_type="Incident Submitted",
            link_url=f"/admin/incidents/{report.id}"
        )

        return report

    @staticmethod
    def update_incident_status(
        incident_id: int,
        new_status: str,
        admin_id: int,
        admin_name: str,
        admin_email: str,
        resolution_notes: str = "",
        ip_address: str = ""
    ) -> Optional[IncidentReport]:
        incident = IncidentRepository.get_by_id(incident_id)
        if not incident:
            return None

        old_status = incident.status
        incident = IncidentRepository.update_status(
            incident=incident,
            status=new_status,
            admin_id=admin_id,
            resolution_notes=resolution_notes
        )

        # Add timeline entry
        timeline_note = f"Status updated from {old_status} to {new_status}."
        if resolution_notes:
            timeline_note += f" Notes: {resolution_notes}"

        IncidentRepository.add_timeline_entry(
            incident_id=incident.id,
            actor_name=admin_name,
            actor_role="ADMIN",
            action=f"STATUS_{new_status}",
            notes=timeline_note
        )

        AuditRepository.log(
            action="INCIDENT_STATUS_CHANGED",
            category="INCIDENT",
            user_id=admin_id,
            user_email=admin_email,
            details=f"Incident #{incident.id} status changed from {old_status} to {new_status}",
            ip_address=ip_address
        )

        # Notify the user who reported the incident
        NotificationRepository.create_notification(
            user_id=incident.user_id,
            title=f"Incident #{incident.id} Status: {new_status}",
            message=f"An administrator updated your incident report to {new_status}. {resolution_notes}",
            notification_type="Incident Status Changed",
            link_url=f"/incidents/{incident.id}"
        )

        return incident
