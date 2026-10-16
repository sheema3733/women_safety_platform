import io
import csv
import json
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import select, desc
from app.database import db_session
from app.models.sos import SOSEvent
from app.models.incident import IncidentReport
from app.models.user import User, UserActivity
from app.models.resource import EmergencyResource
from app.models.tip import SafetyTip

class ReportService:
    @staticmethod
    def generate_sos_report(status_filter: str = "") -> List[Dict[str, Any]]:
        stmt = select(SOSEvent).join(User).order_by(desc(SOSEvent.created_at))
        if status_filter:
            stmt = stmt.where(SOSEvent.status == status_filter.upper())
        events = db_session.execute(stmt).scalars().all()

        rows = []
        for e in events:
            rows.append({
                "SOS ID": f"#{e.id}",
                "User Email": e.user.email if e.user else "N/A",
                "User Name": e.user.full_name if e.user else "N/A",
                "Status": e.status,
                "Trigger Type": e.trigger_type,
                "Location Note": e.address_note or "N/A",
                "Coordinates": f"{e.latitude}, {e.longitude}" if e.latitude else "N/A",
                "Triggered At": e.created_at.strftime("%Y-%m-%d %H:%M:%S") if e.created_at else "",
                "Resolved At": e.resolved_at.strftime("%Y-%m-%d %H:%M:%S") if e.resolved_at else "N/A",
                "Resolution Notes": e.resolution_notes or "N/A"
            })
        return rows

    @staticmethod
    def generate_incident_report(category_filter: str = "", severity_filter: str = "", status_filter: str = "") -> List[Dict[str, Any]]:
        stmt = select(IncidentReport).join(User, IncidentReport.user_id == User.id).order_by(desc(IncidentReport.created_at))
        if category_filter:
            stmt = stmt.where(IncidentReport.incident_type == category_filter)
        if severity_filter:
            stmt = stmt.where(IncidentReport.severity == severity_filter)
        if status_filter:
            stmt = stmt.where(IncidentReport.status == status_filter)

        incidents = db_session.execute(stmt).scalars().all()
        rows = []
        for inc in incidents:
            rows.append({
                "Incident ID": f"#{inc.id}",
                "User Email": inc.user.email if inc.user else "N/A",
                "Incident Type": inc.incident_type,
                "Date/Time": inc.incident_date.strftime("%Y-%m-%d %H:%M") if inc.incident_date else "",
                "Location Area": inc.general_area,
                "Severity": inc.severity,
                "Status": inc.status,
                "Description": inc.description,
                "Resolution Notes": inc.resolution_notes or "N/A"
            })
        return rows

    @staticmethod
    def generate_resource_report(category_filter: str = "", city_filter: str = "") -> List[Dict[str, Any]]:
        stmt = select(EmergencyResource).order_by(EmergencyResource.city, EmergencyResource.category)
        if category_filter:
            stmt = stmt.where(EmergencyResource.category == category_filter)
        if city_filter:
            stmt = stmt.where(EmergencyResource.city == city_filter)

        resources = db_session.execute(stmt).scalars().all()
        rows = []
        for r in resources:
            rows.append({
                "Resource ID": f"#{r.id}",
                "Name": r.name,
                "Category": r.category,
                "City": r.city,
                "General Area": r.general_area,
                "Contact Phone": r.demo_phone,
                "Status": "Active" if r.is_active else "Inactive"
            })
        return rows

    @staticmethod
    def to_csv(data: List[Dict[str, Any]]) -> str:
        if not data:
            return ""
        output = io.StringIO()
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        return output.getvalue()

    @staticmethod
    def to_json(data: List[Dict[str, Any]]) -> str:
        return json.dumps(data, indent=2, default=str)
