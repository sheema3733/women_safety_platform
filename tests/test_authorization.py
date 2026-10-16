import pytest

def test_admin_route_forbidden_for_user(auth_user_client):
    response = auth_user_client.get("/admin/dashboard")
    assert response.status_code == 403

def test_admin_route_accessible_for_admin(auth_admin_client):
    response = auth_admin_client.get("/admin/dashboard")
    assert response.status_code == 200
    assert b"Central Monitoring & Command Center" in response.data

def test_unauthenticated_access_redirects(client):
    response = client.get("/user/dashboard")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
