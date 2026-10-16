from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.security.auth_decorators import login_required, role_required, get_current_user
from app.services.analytics_service import AnalyticsService
from app.services.incident_service import IncidentService
from app.services.sos_service import SOSService
from app.repositories.user_repo import UserRepository
from app.repositories.sos_repo import SOSRepository
from app.repositories.incident_repo import IncidentRepository
from app.repositories.resource_repo import ResourceRepository
from app.repositories.tip_repo import TipRepository
from app.repositories.audit_repo import AuditRepository
from app.repositories.notification_repo import NotificationRepository
from app.database import db_session
from app.models.settings import SystemSetting
from app.validators.forms import (
    validate_resource,
    validate_safety_tip,
    ValidationError,
    RESOURCE_CATEGORIES,
    TIP_CATEGORIES,
    INCIDENT_TYPES,
    SEVERITIES,
    INCIDENT_STATUSES
)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Ensure all admin routes require login and ADMIN role
@admin_bp.before_request
@login_required
@role_required("ADMIN")
def require_admin():
    pass

@admin_bp.route("/dashboard")
def dashboard():
    admin = get_current_user()
    kpis = AnalyticsService.get_dashboard_kpis()
    recent_sos, _ = SOSRepository.list_all_sos(page=1, per_page=5)
    recent_incidents, _ = IncidentRepository.list_all_incidents(page=1, per_page=5)
    recent_logs, _ = AuditRepository.list_logs(page=1, per_page=6)

    return render_template(
        "admin/dashboard.html",
        admin=admin,
        kpis=kpis,
        recent_sos=recent_sos,
        recent_incidents=recent_incidents,
        recent_logs=recent_logs
    )

# --- USER MANAGEMENT ---
@admin_bp.route("/users")
def users():
    search = request.args.get("q", "").strip()
    role_filter = request.args.get("role", "").strip()
    status_filter = request.args.get("status", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 15

    users_list, total = UserRepository.list_users(
        search=search,
        role_filter=role_filter,
        status_filter=status_filter,
        page=page,
        per_page=per_page
    )

    return render_template(
        "admin/users.html",
        users=users_list,
        total=total,
        page=page,
        per_page=per_page,
        search=search,
        role_filter=role_filter,
        status_filter=status_filter
    )

@admin_bp.route("/users/toggle-status/<int:user_id>", methods=["POST"])
def toggle_user_status(user_id: int):
    admin = get_current_user()
    user = UserRepository.get_by_id(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin.users"))

    if user.id == admin.id:
        flash("You cannot deactivate your own administrator account.", "warning")
        return redirect(url_for("admin.users"))

    new_status = not user.is_active
    UserRepository.update_user(user, is_active=new_status)
    status_label = "activated" if new_status else "deactivated"

    AuditRepository.log(
        action="USER_STATUS_CHANGE",
        category="USER_MGMT",
        user_id=admin.id,
        user_email=admin.email,
        details=f"User {user.email} (ID #{user.id}) was {status_label} by Admin {admin.email}",
        ip_address=request.remote_addr or ""
    )

    flash(f"User '{user.email}' has been {status_label}.", "success")
    return redirect(url_for("admin.users"))

# --- SOS MANAGEMENT ---
@admin_bp.route("/sos")
def sos_management():
    search = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 15

    sos_list, total = SOSRepository.list_all_sos(
        search=search,
        status_filter=status_filter,
        page=page,
        per_page=per_page
    )

    return render_template(
        "admin/sos.html",
        sos_list=sos_list,
        total=total,
        page=page,
        per_page=per_page,
        search=search,
        status_filter=status_filter
    )

@admin_bp.route("/sos/resolve/<int:sos_id>", methods=["POST"])
def resolve_sos(sos_id: int):
    admin = get_current_user()
    notes = request.form.get("resolution_notes", "Resolved by Admin intervention.").strip()
    SOSService.resolve_sos(
        sos_id=sos_id,
        actor_email=admin.email,
        resolved_by="ADMIN",
        resolution_notes=notes,
        ip_address=request.remote_addr or ""
    )
    flash(f"SOS #{sos_id} marked as RESOLVED by administrator.", "success")
    return redirect(url_for("admin.sos_management"))

@admin_bp.route("/sos/cancel/<int:sos_id>", methods=["POST"])
def cancel_sos(sos_id: int):
    admin = get_current_user()
    reason = request.form.get("cancel_reason", "Cancelled by Admin.").strip()
    SOSService.cancel_sos(
        sos_id=sos_id,
        actor_email=admin.email,
        cancelled_by="ADMIN",
        cancel_reason=reason,
        ip_address=request.remote_addr or ""
    )
    flash(f"SOS #{sos_id} marked as CANCELLED by administrator.", "info")
    return redirect(url_for("admin.sos_management"))

# --- INCIDENT MANAGEMENT ---
@admin_bp.route("/incidents")
def incidents():
    search = request.args.get("q", "").strip()
    type_filter = request.args.get("type", "").strip()
    severity_filter = request.args.get("severity", "").strip()
    status_filter = request.args.get("status", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 15

    incidents_list, total = IncidentRepository.list_all_incidents(
        search=search,
        type_filter=type_filter,
        severity_filter=severity_filter,
        status_filter=status_filter,
        page=page,
        per_page=per_page
    )

    return render_template(
        "admin/incidents.html",
        incidents=incidents_list,
        total=total,
        page=page,
        per_page=per_page,
        search=search,
        type_filter=type_filter,
        severity_filter=severity_filter,
        status_filter=status_filter,
        incident_types=INCIDENT_TYPES,
        severities=SEVERITIES,
        statuses=INCIDENT_STATUSES
    )

@admin_bp.route("/incidents/<int:incident_id>", methods=["GET", "POST"])
def incident_detail(incident_id: int):
    admin = get_current_user()
    incident = IncidentRepository.get_by_id(incident_id)

    if not incident:
        flash("Incident report not found.", "danger")
        return redirect(url_for("admin.incidents"))

    if request.method == "POST":
        new_status = request.form.get("status")
        notes = request.form.get("resolution_notes", "").strip()
        if new_status in INCIDENT_STATUSES:
            IncidentService.update_incident_status(
                incident_id=incident.id,
                new_status=new_status,
                admin_id=admin.id,
                admin_name=admin.full_name,
                admin_email=admin.email,
                resolution_notes=notes,
                ip_address=request.remote_addr or ""
            )
            flash(f"Incident #{incident.id} status updated to {new_status}.", "success")
            return redirect(url_for("admin.incident_detail", incident_id=incident.id))

    return render_template(
        "admin/incident_detail.html",
        incident=incident,
        statuses=INCIDENT_STATUSES,
        is_admin_view=True
    )

# --- EMERGENCY RESOURCES MANAGEMENT ---
@admin_bp.route("/resources")
def resources():
    search = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    city = request.args.get("city", "").strip()
    status_filter = request.args.get("status", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 15

    res_list, total = ResourceRepository.list_all_resources(
        search=search,
        category=category,
        city=city,
        status_filter=status_filter,
        page=page,
        per_page=per_page
    )

    cities = ResourceRepository.get_distinct_cities()

    return render_template(
        "admin/resources.html",
        resources=res_list,
        total=total,
        page=page,
        per_page=per_page,
        search=search,
        category=category,
        city=city,
        status_filter=status_filter,
        categories=RESOURCE_CATEGORIES,
        cities=cities
    )

@admin_bp.route("/resources/create", methods=["GET", "POST"])
def resource_create():
    admin = get_current_user()
    errors = {}
    form_data = {}

    if request.method == "POST":
        form_data = request.form.to_dict()
        try:
            val = validate_resource(form_data)
            res = ResourceRepository.create_resource(
                name=val["name"],
                category=val["category"],
                city=val["city"],
                general_area=val["general_area"],
                demo_phone=val["demo_phone"],
                description=val["description"],
                latitude=val["latitude"],
                longitude=val["longitude"],
                is_active=val["is_active"]
            )
            AuditRepository.log(
                action="RESOURCE_CREATED",
                category="RESOURCE",
                user_id=admin.id,
                user_email=admin.email,
                details=f"Created resource #{res.id}: {res.name} ({res.category})",
                ip_address=request.remote_addr or ""
            )
            flash(f"Resource '{res.name}' created successfully.", "success")
            return redirect(url_for("admin.resources"))
        except ValidationError as ve:
            errors = ve.errors

    return render_template(
        "admin/resource_form.html",
        errors=errors,
        form_data=form_data,
        categories=RESOURCE_CATEGORIES,
        is_edit=False
    )

@admin_bp.route("/resources/edit/<int:resource_id>", methods=["GET", "POST"])
def resource_edit(resource_id: int):
    admin = get_current_user()
    resource = ResourceRepository.get_by_id(resource_id)
    if not resource:
        flash("Resource not found.", "warning")
        return redirect(url_for("admin.resources"))

    errors = {}
    form_data = {
        "name": resource.name,
        "category": resource.category,
        "city": resource.city,
        "general_area": resource.general_area,
        "demo_phone": resource.demo_phone,
        "description": resource.description or "",
        "latitude": resource.latitude or "",
        "longitude": resource.longitude or "",
        "is_active": resource.is_active
    }

    if request.method == "POST":
        form_data = request.form.to_dict()
        try:
            val = validate_resource(form_data)
            ResourceRepository.update_resource(
                resource=resource,
                name=val["name"],
                category=val["category"],
                city=val["city"],
                general_area=val["general_area"],
                demo_phone=val["demo_phone"],
                description=val["description"],
                latitude=val["latitude"],
                longitude=val["longitude"],
                is_active=val["is_active"]
            )
            AuditRepository.log(
                action="RESOURCE_UPDATED",
                category="RESOURCE",
                user_id=admin.id,
                user_email=admin.email,
                details=f"Updated resource #{resource.id}: {resource.name}",
                ip_address=request.remote_addr or ""
            )
            flash(f"Resource '{resource.name}' updated successfully.", "success")
            return redirect(url_for("admin.resources"))
        except ValidationError as ve:
            errors = ve.errors

    return render_template(
        "admin/resource_form.html",
        errors=errors,
        form_data=form_data,
        resource=resource,
        categories=RESOURCE_CATEGORIES,
        is_edit=True
    )

@admin_bp.route("/resources/delete/<int:resource_id>", methods=["POST"])
def resource_delete(resource_id: int):
    admin = get_current_user()
    resource = ResourceRepository.get_by_id(resource_id)
    if resource:
        name = resource.name
        ResourceRepository.delete_resource(resource)
        AuditRepository.log(
            action="RESOURCE_DELETED",
            category="RESOURCE",
            user_id=admin.id,
            user_email=admin.email,
            details=f"Deleted resource: {name}",
            ip_address=request.remote_addr or ""
        )
        flash(f"Resource '{name}' deleted.", "info")
    return redirect(url_for("admin.resources"))

# --- SAFETY CONTENT / TIPS MANAGEMENT ---
@admin_bp.route("/tips")
def tips():
    search = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    status_filter = request.args.get("status", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 15

    tips_list, total = TipRepository.list_all_tips(
        search=search,
        category=category,
        status_filter=status_filter,
        page=page,
        per_page=per_page
    )

    return render_template(
        "admin/tips.html",
        tips=tips_list,
        total=total,
        page=page,
        per_page=per_page,
        search=search,
        category=category,
        status_filter=status_filter,
        categories=TIP_CATEGORIES
    )

@admin_bp.route("/tips/create", methods=["GET", "POST"])
def tip_create():
    admin = get_current_user()
    errors = {}
    form_data = {}

    if request.method == "POST":
        form_data = request.form.to_dict()
        try:
            val = validate_safety_tip(form_data)
            tip = TipRepository.create_tip(
                title=val["title"],
                category=val["category"],
                summary=val["summary"],
                content=val["content"],
                read_time_minutes=val["read_time_minutes"],
                is_published=val["is_published"]
            )
            AuditRepository.log(
                action="TIP_CREATED",
                category="SAFETY_TIP",
                user_id=admin.id,
                user_email=admin.email,
                details=f"Created tip #{tip.id}: {tip.title}",
                ip_address=request.remote_addr or ""
            )
            flash(f"Safety tip '{tip.title}' created.", "success")
            return redirect(url_for("admin.tips"))
        except ValidationError as ve:
            errors = ve.errors

    return render_template(
        "admin/tip_form.html",
        errors=errors,
        form_data=form_data,
        categories=TIP_CATEGORIES,
        is_edit=False
    )

@admin_bp.route("/tips/edit/<int:tip_id>", methods=["GET", "POST"])
def tip_edit(tip_id: int):
    admin = get_current_user()
    tip = TipRepository.get_by_id(tip_id)
    if not tip:
        flash("Safety tip not found.", "warning")
        return redirect(url_for("admin.tips"))

    errors = {}
    form_data = {
        "title": tip.title,
        "category": tip.category,
        "summary": tip.summary,
        "content": tip.content,
        "read_time_minutes": tip.read_time_minutes,
        "is_published": tip.is_published
    }

    if request.method == "POST":
        form_data = request.form.to_dict()
        try:
            val = validate_safety_tip(form_data)
            TipRepository.update_tip(
                tip=tip,
                title=val["title"],
                category=val["category"],
                summary=val["summary"],
                content=val["content"],
                read_time_minutes=val["read_time_minutes"],
                is_published=val["is_published"]
            )
            AuditRepository.log(
                action="TIP_UPDATED",
                category="SAFETY_TIP",
                user_id=admin.id,
                user_email=admin.email,
                details=f"Updated tip #{tip.id}: {tip.title}",
                ip_address=request.remote_addr or ""
            )
            flash(f"Safety tip '{tip.title}' updated.", "success")
            return redirect(url_for("admin.tips"))
        except ValidationError as ve:
            errors = ve.errors

    return render_template(
        "admin/tip_form.html",
        errors=errors,
        form_data=form_data,
        tip=tip,
        categories=TIP_CATEGORIES,
        is_edit=True
    )

@admin_bp.route("/tips/delete/<int:tip_id>", methods=["POST"])
def tip_delete(tip_id: int):
    admin = get_current_user()
    tip = TipRepository.get_by_id(tip_id)
    if tip:
        title = tip.title
        TipRepository.delete_tip(tip)
        AuditRepository.log(
            action="TIP_DELETED",
            category="SAFETY_TIP",
            user_id=admin.id,
            user_email=admin.email,
            details=f"Deleted tip: {title}",
            ip_address=request.remote_addr or ""
        )
        flash(f"Safety tip '{title}' removed.", "info")
    return redirect(url_for("admin.tips"))

# --- AUDIT LOGS ---
@admin_bp.route("/audit-logs")
def audit_logs():
    search = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 20

    logs, total = AuditRepository.list_logs(
        search=search,
        category=category,
        page=page,
        per_page=per_page
    )
    categories = AuditRepository.get_categories()

    return render_template(
        "admin/audit_logs.html",
        logs=logs,
        total=total,
        page=page,
        per_page=per_page,
        search=search,
        selected_category=category,
        categories=categories
    )

# --- SYSTEM SETTINGS ---
@admin_bp.route("/settings", methods=["GET", "POST"])
def settings():
    admin = get_current_user()
    if request.method == "POST":
        for key, val in request.form.items():
            if key == "csrf_token":
                continue
            setting = db_session.query(SystemSetting).filter_by(key=key).first()
            if setting:
                setting.value = val
            else:
                db_session.add(SystemSetting(key=key, value=val))
        db_session.commit()
        AuditRepository.log(
            action="SETTINGS_UPDATED",
            category="SETTINGS",
            user_id=admin.id,
            user_email=admin.email,
            details="Admin updated system settings",
            ip_address=request.remote_addr or ""
        )
        flash("Platform settings updated successfully.", "success")
        return redirect(url_for("admin.settings"))

    settings_list = db_session.query(SystemSetting).all()
    return render_template("admin/settings.html", settings=settings_list)
