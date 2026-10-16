from app.database import db_session
from app.models.user import User
from app.services.analytics_service import AnalyticsService

def test_admin_toggle_user_status(auth_admin_client, test_user):
    assert test_user.is_active is True

    # Deactivate
    response = auth_admin_client.post(f"/admin/users/toggle-status/{test_user.id}", follow_redirects=True)
    assert response.status_code == 200
    u = db_session.get(User, test_user.id)
    assert u.is_active is False

    # Reactivate
    response2 = auth_admin_client.post(f"/admin/users/toggle-status/{test_user.id}", follow_redirects=True)
    assert response2.status_code == 200
    u2 = db_session.get(User, test_user.id)
    assert u2.is_active is True

def test_analytics_kpi_and_chart_data(auth_admin_client):
    kpis = AnalyticsService.get_dashboard_kpis()
    assert "total_users" in kpis
    assert "active_sos" in kpis
    assert "total_incidents" in kpis

    resp = auth_admin_client.get("/analytics/data")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "sos_status" in data
    assert "incident_category" in data

def test_reports_exports(auth_admin_client):
    # CSV export
    csv_resp = auth_admin_client.get("/reports/?type=sos&format=csv")
    assert csv_resp.status_code == 200
    assert "text/csv" in csv_resp.headers["Content-Type"]

    # JSON export
    json_resp = auth_admin_client.get("/reports/?type=incidents&format=json")
    assert json_resp.status_code == 200
    assert "application/json" in json_resp.headers["Content-Type"]

def test_admin_audit_logs(auth_admin_client):
    response = auth_admin_client.get("/admin/audit-logs")
    assert response.status_code == 200
    assert b"Security & System Audit Logs" in response.data
