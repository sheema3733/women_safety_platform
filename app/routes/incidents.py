from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.security.auth_decorators import login_required, get_current_user
from app.repositories.incident_repo import IncidentRepository
from app.services.incident_service import IncidentService
from app.validators.forms import validate_incident_report, ValidationError, INCIDENT_TYPES, SEVERITIES

incidents_bp = Blueprint("incidents", __name__, url_prefix="/incidents")

@incidents_bp.route("/")
@login_required
def index():
    user = get_current_user()
    search = request.args.get("q", "").strip()
    type_filter = request.args.get("type", "").strip()
    severity_filter = request.args.get("severity", "").strip()
    status_filter = request.args.get("status", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 10

    reports, total = IncidentRepository.get_user_incidents(
        user_id=user.id,
        search=search,
        type_filter=type_filter,
        severity_filter=severity_filter,
        status_filter=status_filter,
        page=page,
        per_page=per_page
    )

    return render_template(
        "incidents/index.html",
        reports=reports,
        total=total,
        page=page,
        per_page=per_page,
        search=search,
        type_filter=type_filter,
        severity_filter=severity_filter,
        status_filter=status_filter,
        incident_types=INCIDENT_TYPES,
        severities=SEVERITIES
    )

@incidents_bp.route("/report", methods=["GET", "POST"])
@login_required
def submit():
    user = get_current_user()
    errors = {}
    form_data = {}

    if request.method == "POST":
        form_data = request.form.to_dict()
        try:
            validated = validate_incident_report(form_data)
            ip_address = request.remote_addr or ""
            report = IncidentService.submit_report(
                user_id=user.id,
                validated_data=validated,
                ip_address=ip_address
            )
            flash(f"Incident report #{report.id} submitted successfully. An administrator will review it.", "success")
            return redirect(url_for("incidents.detail", incident_id=report.id))
        except ValidationError as ve:
            errors = ve.errors

    return render_template(
        "incidents/submit.html",
        errors=errors,
        form_data=form_data,
        incident_types=INCIDENT_TYPES,
        severities=SEVERITIES
    )

@incidents_bp.route("/<int:incident_id>")
@login_required
def detail(incident_id: int):
    user = get_current_user()
    incident = IncidentRepository.get_by_id(incident_id)

    if not incident or (incident.user_id != user.id and not user.is_admin):
        flash("Incident report not found or access restricted.", "warning")
        return redirect(url_for("incidents.index"))

    return render_template("incidents/detail.html", incident=incident, is_admin_view=False)
