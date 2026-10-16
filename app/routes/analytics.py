from flask import Blueprint, render_template, jsonify
from app.security.auth_decorators import login_required, role_required
from app.services.analytics_service import AnalyticsService

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")

@analytics_bp.before_request
@login_required
@role_required("ADMIN")
def require_admin():
    pass

@analytics_bp.route("/")
def index():
    kpis = AnalyticsService.get_dashboard_kpis()
    chart_data = AnalyticsService.get_charts_data()
    return render_template("analytics/index.html", kpis=kpis, charts=chart_data)

@analytics_bp.route("/data")
def data_endpoint():
    return jsonify(AnalyticsService.get_charts_data())
