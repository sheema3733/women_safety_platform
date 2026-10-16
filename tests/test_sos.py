from app.database import db_session
from app.models.sos import SOSEvent, SOSAuditLog
from app.models.notification import Notification

def test_sos_trigger_and_active_state(auth_user_client, test_user):
    response = auth_user_client.post("/sos/trigger", data={
        "trigger_type": "MANUAL",
        "address_note": "Corner of 4th and Elm",
        "emergency_notes": "Suspicious person following"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Active Assistance Command Station" in response.data

    sos = db_session.query(SOSEvent).filter_by(user_id=test_user.id, status="ACTIVE").first()
    assert sos is not None
    assert sos.address_note == "Corner of 4th and Elm"
    assert sos.is_active is True

    # Verify notification created
    notif = db_session.query(Notification).filter_by(user_id=test_user.id, notification_type="SOS Created").first()
    assert notif is not None

def test_sos_resolve_workflow(auth_user_client, test_user):
    # Trigger first
    auth_user_client.post("/sos/trigger", data={"address_note": "Station area"})
    sos = db_session.query(SOSEvent).filter_by(user_id=test_user.id, status="ACTIVE").first()
    assert sos is not None

    # Resolve
    response = auth_user_client.post(f"/sos/resolve/{sos.id}", data={
        "resolution_notes": "Boarded safe bus. Family informed."
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"SOS event resolved successfully" in response.data

    db_session.refresh(sos)
    assert sos.status == "RESOLVED"
    assert sos.resolved_at is not None
    assert "Boarded safe bus" in sos.resolution_notes

def test_sos_cancel_workflow(auth_user_client, test_user):
    # Trigger
    auth_user_client.post("/sos/trigger", data={"address_note": "Campus quad"})
    sos = db_session.query(SOSEvent).filter_by(user_id=test_user.id, status="ACTIVE").first()

    # Cancel
    response = auth_user_client.post(f"/sos/cancel/{sos.id}", data={
        "cancel_reason": "False alarm - phone slipped"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"SOS alert cancelled" in response.data

    db_session.refresh(sos)
    assert sos.status == "CANCELLED"
