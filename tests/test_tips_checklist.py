from app.database import db_session
from app.models.checklist import ChecklistItem, UserChecklistProgress
from app.models.contact import EmergencyContact
from app.models.tip import SafetyTip, TipView
from app.services.readiness_service import ReadinessService

def test_browse_safety_tips(client):
    response = client.get("/tips/")
    assert response.status_code == 200
    assert b"Night Transit Safety" in response.data

def test_view_tip_marks_viewed(auth_user_client, test_user):
    tip = db_session.query(SafetyTip).first()
    assert tip is not None

    response = auth_user_client.get(f"/tips/{tip.id}")
    assert response.status_code == 200
    assert tip.title.encode() in response.data

    view = db_session.query(TipView).filter_by(user_id=test_user.id, tip_id=tip.id).first()
    assert view is not None

def test_checklist_toggle(auth_user_client, test_user):
    item = db_session.query(ChecklistItem).first()
    assert item is not None

    # Toggle to complete
    resp = auth_user_client.post(f"/checklist/toggle/{item.id}", json={"is_completed": True})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["is_completed"] is True
    assert data["stats"]["completed"] >= 1

    progress = db_session.query(UserChecklistProgress).filter_by(
        user_id=test_user.id,
        item_id=item.id
    ).first()
    assert progress.is_completed is True

def test_safety_readiness_score_calculation(test_user):
    # Add 2 contacts (1 trusted)
    c1 = EmergencyContact(user_id=test_user.id, name="Mom", relationship="Mother", phone="123", is_trusted=True, priority_order=1)
    c2 = EmergencyContact(user_id=test_user.id, name="Friend", relationship="Friend", phone="456", is_trusted=False, priority_order=2)
    db_session.add_all([c1, c2])

    # Complete 2 checklist items
    items = db_session.query(ChecklistItem).all()
    for it in items[:2]:
        db_session.add(UserChecklistProgress(user_id=test_user.id, item_id=it.id, is_completed=True))

    db_session.commit()

    readiness = ReadinessService.calculate_score(test_user.id)
    assert readiness["score"] > 0
    assert "disclaimer" in readiness
    assert readiness["breakdown"]["contacts"]["has_trusted"] is True
