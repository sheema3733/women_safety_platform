from flask import Blueprint, render_template, request, Response
from app.security.auth_decorators import login_required, role_required
from app.services.report_service import ReportService
from app.validators.forms import INCIDENT_TYPES, SEVERITIES, RESOURCE_CATEGORIES

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")

@reports_bp.before_request
@login_required
@role_required("ADMIN")
def require_admin():
    pass

@reports_bp.route("/")
def index():
    report_type = request.args.get("type", "sos")
    format_type = request.args.get("format", "view")

    status_filter = request.args.get("status", "")
    category_filter = request.args.get("category", "")
    severity_filter = request.args.get("severity", "")

    if report_type == "incidents":
        data = ReportService.generate_incident_report(
            category_filter=category_filter,
            severity_filter=severity_filter,
            status_filter=status_filter
        )
        title = "Incidents Summary Report"
    elif report_type == "resources":
        data = ReportService.generate_resource_report(
            category_filter=category_filter
        )
        title = "Emergency Resources Report"
    else: # Default SOS
        report_type = "sos"
        data = ReportService.generate_sos_report(status_filter=status_filter)
        title = "SOS Emergency Events Report"

    # Export handlers
    if format_type == "csv":
        csv_data = ReportService.to_csv(data)
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename=report_{report_type}.csv"}
        )
    elif format_type == "json":
        json_data = ReportService.to_json(data)
        return Response(
            json_data,
            mimetype="application/json",
            headers={"Content-Disposition": f"attachment;filename=report_{report_type}.json"}
        )
    elif format_type == "print":
        return render_template(
            "reports/print_view.html",
            title=title,
            report_type=report_type,
            data=data
        )

    return render_template(
        "reports/index.html",
        title=title,
        report_type=report_type,
        data=data,
        status_filter=status_filter,
        category_filter=category_filter,
        severity_filter=severity_filter,
        incident_types=INCIDENT_TYPES,
        severities=SEVERITIES,
        resource_categories=RESOURCE_CATEGORIES
    )
