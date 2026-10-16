from typing import Optional, Dict, Any, List
from app.repositories.sos_repo import SOSRepository
from app.repositories.user_repo import UserRepository
from app.repositories.contact_repo import ContactRepository
from app.repositories.resource_repo import ResourceRepository
from app.repositories.notification_repo import NotificationRepository
from app.repositories.audit_repo import AuditRepository
from app.models.sos import SOSEvent

EMERGENCY_GUIDANCE_STEPS = [
    {
        "step": 1,
        "title": "Move to a Visible, Public Location",
        "detail": "If possible, enter a brightly lit store, public transit station, reception lobby, or well-populated area."
    },
    {
        "step": 2,
        "title": "Call Official Emergency Services Directly",
        "detail": "Dial your local emergency number (e.g., 112 / 1091 / 911) immediately if you are facing immediate physical harm."
    },
    {
        "step": 3,
        "title": "Contact Your Trusted Emergency Contacts",
        "detail": "Use the one-touch call buttons below to reach your designated family members or friends."
    },
    {
        "step": 4,
        "title": "Stay on the Line and Keep Your Phone Charged",
        "detail": "Keep your phone accessible, maintain awareness of your surroundings, and avoid isolated pathways."
    },
    {
        "step": 5,
        "title": "Locate Verified Safe Havens Nearby",
        "detail": "Refer to the emergency resources list below for verified police stations, hospitals, and support centers."
    }
]

class SOSService:
    @staticmethod
    def trigger_sos(
        user_id: int,
        trigger_type: str = "MANUAL",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        address_note: str = "",
        emergency_notes: str = "",
        ip_address: str = ""
    ) -> SOSEvent:
        # Check if user already has an active SOS
        existing = SOSRepository.get_active_for_user(user_id)
        if existing:
            return existing

        user = UserRepository.get_by_id(user_id)
        user_email = user.email if user else f"user_{user_id}"
        user_name = user.full_name if user else "A user"

        # Create SOS event
        sos = SOSRepository.create_event(
            user_id=user_id,
            trigger_type=trigger_type,
            latitude=latitude,
            longitude=longitude,
            address_note=address_note,
            emergency_notes=emergency_notes
        )

        # Log to SOS audit trail
        SOSRepository.add_audit_log(
            sos_id=sos.id,
            action="ACTIVATED",
            actor_email=user_email,
            notes=f"Emergency SOS triggered ({trigger_type}). Location: {address_note or 'Browser GPS'}"
        )

        # Platform audit log
        AuditRepository.log(
            action="SOS_ACTIVATED",
            category="SOS",
            user_id=user_id,
            user_email=user_email,
            details=f"SOS #{sos.id} activated. Notes: {emergency_notes or 'None'}",
            ip_address=ip_address
        )

        # User activity log
        UserRepository.log_activity(
            user_id=user_id,
            action="SOS Activated",
            details=f"Emergency alert triggered (ID #{sos.id})",
            ip_address=ip_address
        )

        # Internal notifications
        NotificationRepository.create_notification(
            user_id=user_id,
            title="Emergency SOS Activated",
            message=f"SOS #{sos.id} is now ACTIVE. Access emergency guidance and contact your trusted contacts immediately.",
            notification_type="SOS Created",
            link_url=f"/sos/active/{sos.id}"
        )

        # Alert platform administrators
        NotificationRepository.notify_admins(
            title=f"URGENT: SOS Alert Activated by {user_name}",
            message=f"User {user_name} ({user_email}) triggered SOS #{sos.id} at {address_note or 'coordinates reported'}.",
            notification_type="SOS Created",
            link_url=f"/admin/sos"
        )

        return sos

    @staticmethod
    def resolve_sos(
        sos_id: int,
        actor_email: str,
        resolved_by: str = "USER",
        resolution_notes: str = "",
        ip_address: str = ""
    ) -> Optional[SOSEvent]:
        sos = SOSRepository.get_by_id(sos_id)
        if not sos or sos.status != "ACTIVE":
            return None

        sos = SOSRepository.update_status(
            sos=sos,
            status="RESOLVED",
            resolved_by=resolved_by,
            resolution_notes=resolution_notes
        )

        SOSRepository.add_audit_log(
            sos_id=sos.id,
            action="RESOLVED",
            actor_email=actor_email,
            notes=f"Resolved by {resolved_by}. Notes: {resolution_notes}"
        )

        AuditRepository.log(
            action="SOS_RESOLVED",
            category="SOS",
            user_id=sos.user_id,
            user_email=actor_email,
            details=f"SOS #{sos.id} resolved by {resolved_by}. Notes: {resolution_notes}",
            ip_address=ip_address
        )

        UserRepository.log_activity(
            user_id=sos.user_id,
            action="SOS Resolved",
            details=f"SOS #{sos.id} marked as RESOLVED",
            ip_address=ip_address
        )

        # Notify user
        NotificationRepository.create_notification(
            user_id=sos.user_id,
            title="SOS Alert Resolved",
            message=f"SOS #{sos.id} has been marked as resolved. We hope you are safe.",
            notification_type="SOS Resolved",
            link_url=f"/sos/history"
        )

        return sos

    @staticmethod
    def cancel_sos(
        sos_id: int,
        actor_email: str,
        cancelled_by: str = "USER",
        cancel_reason: str = "Cancelled by user (False Alarm)",
        ip_address: str = ""
    ) -> Optional[SOSEvent]:
        sos = SOSRepository.get_by_id(sos_id)
        if not sos or sos.status != "ACTIVE":
            return None

        sos = SOSRepository.update_status(
            sos=sos,
            status="CANCELLED",
            resolved_by=cancelled_by,
            resolution_notes=cancel_reason
        )

        SOSRepository.add_audit_log(
            sos_id=sos.id,
            action="CANCELLED",
            actor_email=actor_email,
            notes=f"Cancelled by {cancelled_by}. Reason: {cancel_reason}"
        )

        AuditRepository.log(
            action="SOS_CANCELLED",
            category="SOS",
            user_id=sos.user_id,
            user_email=actor_email,
            details=f"SOS #{sos.id} cancelled. Reason: {cancel_reason}",
            ip_address=ip_address
        )

        UserRepository.log_activity(
            user_id=sos.user_id,
            action="SOS Cancelled",
            details=f"SOS #{sos.id} cancelled: {cancel_reason}",
            ip_address=ip_address
        )

        NotificationRepository.create_notification(
            user_id=sos.user_id,
            title="SOS Alert Cancelled",
            message=f"SOS #{sos.id} was cancelled ({cancel_reason}).",
            notification_type="SOS Cancelled",
            link_url=f"/sos/history"
        )

        return sos

    @staticmethod
    def get_active_command_data(user_id: int) -> Dict[str, Any]:
        active_sos = SOSRepository.get_active_for_user(user_id)
        trusted_contacts = ContactRepository.get_trusted_for_user(user_id)
        all_contacts = ContactRepository.get_for_user(user_id)
        nearby_resources = ResourceRepository.get_active_resources(limit=6)

        return {
            "active_sos": active_sos,
            "guidance_steps": EMERGENCY_GUIDANCE_STEPS,
            "trusted_contacts": trusted_contacts if trusted_contacts else all_contacts,
            "nearby_resources": nearby_resources
        }
