from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.security.auth_decorators import login_required, role_required, get_current_user
from app.repositories.user_repo import UserRepository
from app.repositories.contact_repo import ContactRepository
from app.repositories.sos_repo import SOSRepository
from app.repositories.incident_repo import IncidentRepository
from app.repositories.checklist_repo import ChecklistRepository
from app.repositories.notification_repo import NotificationRepository
from app.repositories.tip_repo import TipRepository
from app.repositories.resource_repo import ResourceRepository
from app.services.readiness_service import ReadinessService
from app.validators.forms import validate_profile_update, ValidationError

user_bp = Blueprint("user", __name__, url_prefix="/user")

@user_bp.route("/dashboard")
@login_required
@role_required("USER", "ADMIN")
def dashboard():
    user = get_current_user()
    user_id = user.id

    # Readiness Score
    readiness = ReadinessService.calculate_score(user_id)

    # Contacts
    contacts = ContactRepository.get_for_user(user_id)
    contacts_count = len(contacts)

    # Active SOS
    active_sos = SOSRepository.get_active_for_user(user_id)

    # Recent SOS events
    recent_sos, _ = SOSRepository.get_user_history(user_id, page=1, per_page=3)

    # Recent Incidents
    recent_incidents, _ = IncidentRepository.get_user_incidents(user_id, page=1, per_page=3)

    # Checklist Progress
    checklist_stats = ChecklistRepository.get_user_stats(user_id)

    # Recent Notifications
    recent_notifications, _ = NotificationRepository.get_for_user(user_id, page=1, per_page=4)

    # Featured Safety Tips & Resources
    featured_tips = TipRepository.get_published_tips(limit=3)
    featured_resources = ResourceRepository.get_active_resources(limit=3)

    # Recent User Activities
    activities = UserRepository.get_user_activities(user_id, limit=5)

    return render_template(
        "user/dashboard.html",
        user=user,
        readiness=readiness,
        contacts_count=contacts_count,
        active_sos=active_sos,
        recent_sos=recent_sos,
        recent_incidents=recent_incidents,
        checklist_stats=checklist_stats,
        recent_notifications=recent_notifications,
        featured_tips=featured_tips,
        featured_resources=featured_resources,
        activities=activities
    )

@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = get_current_user()
    errors = {}
    
    if request.method == "POST":
        data = request.form.to_dict()
        try:
            validated = validate_profile_update(data)
            UserRepository.update_user(
                user=user,
                full_name=validated["full_name"],
                phone=validated["phone"],
                city=validated["city"]
            )
            session["user_name"] = validated["full_name"]
            UserRepository.log_activity(
                user_id=user.id,
                action="Profile Updated",
                details="Updated personal profile details",
                ip_address=request.remote_addr or ""
            )
            flash("Profile updated successfully.", "success")
            return redirect(url_for("user.profile"))
        except ValidationError as ve:
            errors = ve.errors

    return render_template("user/profile.html", user=user, errors=errors)

@user_bp.route("/history")
@login_required
def history():
    user = get_current_user()
    page = request.args.get("page", 1, type=int)
    per_page = 15

    activities = UserRepository.get_user_activities(user.id, limit=50)
    sos_events, total_sos = SOSRepository.get_user_history(user.id, page=page, per_page=per_page)
    incidents, total_incidents = IncidentRepository.get_user_incidents(user.id, page=page, per_page=per_page)

    return render_template(
        "user/history.html",
        user=user,
        activities=activities,
        sos_events=sos_events,
        incidents=incidents
    )
