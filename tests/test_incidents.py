from app.database import db_session
from app.models.incident import IncidentReport
from app.models.notification import Notification

def test_incident_submission(auth_user_client, test_user):
    response = auth_user_client.post("/incidents/report", data={
        "incident_type": "Harassment",
        "incident_date": "2026-09-15",
        "general_area": "Transit Terminal platform 3",
        "description": "Repeated verbal comments and aggressive pacing nearby.",
        "severity": "MEDIUM"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Incident narrative" in response.data or b"Transit Terminal platform 3" in response.data

    inc = db_session.query(IncidentReport).filter_by(user_id=test_user.id).first()
    assert inc is not None
    assert inc.incident_type == "Harassment"
    assert inc.status == "SUBMITTED"

from app.models.user import User, Role
from app.security.hashing import hash_password

def test_incident_user_isolation(client, test_user, test_admin):
    # Create incident for test_user
    inc = IncidentReport(
        user_id=test_user.id,
        incident_type="Suspicious Activity",
        incident_date=test_user.created_at,
        general_area="Subway North",
        description="Suspicious loitering around turnstiles.",
        severity="LOW",
        status="SUBMITTED"
    )
    db_session.add(inc)

    user_role = db_session.query(Role).filter_by(name="USER").first()
    other_user = User(
        email="seconduser@womensafety.org",
        password_hash=hash_password("Pass@12345"),
        full_name="Second User",
        role_id=user_role.id,
        is_active=True
    )
    db_session.add(other_user)
    db_session.commit()

    # Another user client
    other_client = client
    with other_client.session_transaction() as sess:
        sess["user_id"] = other_user.id
        sess["user_email"] = other_user.email
        sess["user_role"] = "USER"

    response = other_client.get(f"/incidents/{inc.id}", follow_redirects=True)
    assert b"Incident report not found or access restricted" in response.data

def test_admin_incident_status_update(auth_admin_client, test_user, test_admin):
    inc = IncidentReport(
        user_id=test_user.id,
        incident_type="Public Place Safety Issue",
        incident_date=test_user.created_at,
        general_area="Civic Park Alley",
        description="Broken street lamp creating dangerous dark corridor.",
        severity="HIGH",
        status="SUBMITTED"
    )
    db_session.add(inc)
    db_session.commit()

    # Admin updates status to RESOLVED
    response = auth_admin_client.post(f"/admin/incidents/{inc.id}", data={
        "status": "RESOLVED",
        "resolution_notes": "Municipal street lamp replaced and patrol frequency doubled."
    }, follow_redirects=True)

    assert response.status_code == 200
    db_session.refresh(inc)
    assert inc.status == "RESOLVED"
    assert "lamp replaced" in inc.resolution_notes

    # Notification sent to user
    notif = db_session.query(Notification).filter_by(
        user_id=test_user.id,
        notification_type="Incident Status Changed"
    ).first()
    assert notif is not None
