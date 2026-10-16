from app.database import db_session
from app.models.resource import EmergencyResource

def test_browse_resources(client):
    response = client.get("/resources/")
    assert response.status_code == 200
    assert b"City Central Police Station" in response.data

def test_filter_resources_by_category(client):
    response = client.get("/resources/?category=Police+Station")
    assert response.status_code == 200
    assert b"City Central Police Station" in response.data

def test_admin_resource_crud(auth_admin_client):
    # Create
    response = auth_admin_client.post("/admin/resources/create", data={
        "name": "St. Jude Crisis Shelter",
        "category": "Women’s Support Center",
        "city": "Metropolis",
        "general_area": "Harbor Bay",
        "demo_phone": "+1 555-0800",
        "description": "Safe temporary shelter for women.",
        "is_active": "1"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"St. Jude Crisis Shelter" in response.data

    res = db_session.query(EmergencyResource).filter_by(name="St. Jude Crisis Shelter").first()
    assert res is not None
    assert res.city == "Metropolis"

    # Edit
    edit_resp = auth_admin_client.post(f"/admin/resources/edit/{res.id}", data={
        "name": "St. Jude Crisis Shelter - Updated",
        "category": "Women’s Support Center",
        "city": "Metropolis",
        "general_area": "Harbor Bay North",
        "demo_phone": "+1 555-0899",
        "description": "Expanded shelter capacity.",
        "is_active": "1"
    }, follow_redirects=True)
    assert edit_resp.status_code == 200
    db_session.refresh(res)
    assert res.name == "St. Jude Crisis Shelter - Updated"

    # Delete
    del_resp = auth_admin_client.post(f"/admin/resources/delete/{res.id}", follow_redirects=True)
    assert del_resp.status_code == 200
    assert db_session.get(EmergencyResource, res.id) is None
