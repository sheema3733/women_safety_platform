from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.security.auth_decorators import login_required, get_current_user
from app.services.sos_service import SOSService
from app.repositories.sos_repo import SOSRepository
from app.repositories.contact_repo import ContactRepository
from app.repositories.resource_repo import ResourceRepository
from app.config import Config

sos_bp = Blueprint("sos", __name__, url_prefix="/sos")

@sos_bp.route("/")
@login_required
def center():
    user = get_current_user()
    active_sos = SOSRepository.get_active_for_user(user.id)

    # If there is already an active SOS, redirect user to the active view
    if active_sos:
        return redirect(url_for("sos.active_view", sos_id=active_sos.id))

    trusted_contacts = ContactRepository.get_trusted_for_user(user.id)
    all_contacts = ContactRepository.get_for_user(user.id)
    recent_events, _ = SOSRepository.get_user_history(user.id, page=1, per_page=3)

    return render_template(
        "sos/center.html",
        user=user,
        active_sos=active_sos,
        trusted_contacts=trusted_contacts if trusted_contacts else all_contacts,
        recent_events=recent_events,
        disclaimer=Config.DISCLAIMER_TEXT
    )

@sos_bp.route("/trigger", methods=["POST"])
@login_required
def trigger():
    user = get_current_user()
    trigger_type = request.form.get("trigger_type", "MANUAL")
    address_note = request.form.get("address_note", "").strip()
    emergency_notes = request.form.get("emergency_notes", "").strip()

    lat = request.form.get("latitude")
    lng = request.form.get("longitude")
    latitude = float(lat) if lat and lat.strip() else None
    longitude = float(lng) if lng and lng.strip() else None

    ip_address = request.remote_addr or ""

    sos = SOSService.trigger_sos(
        user_id=user.id,
        trigger_type=trigger_type,
        latitude=latitude,
        longitude=longitude,
        address_note=address_note,
        emergency_notes=emergency_notes,
        ip_address=ip_address
    )

    flash("EMERGENCY SOS ACTIVATED. Stay calm and follow safety guidance.", "danger")
    return redirect(url_for("sos.active_view", sos_id=sos.id))

@sos_bp.route("/active/<int:sos_id>")
@login_required
def active_view(sos_id: int):
    user = get_current_user()
    sos = SOSRepository.get_by_id(sos_id)

    # Security check: only author or admin can view
    if not sos or (sos.user_id != user.id and not user.is_admin):
        flash("Emergency alert not found or access denied.", "warning")
        return redirect(url_for("sos.center"))

    if sos.status != "ACTIVE":
        flash(f"This SOS event was already marked as {sos.status}.", "info")
        return redirect(url_for("sos.history"))

    command_data = SOSService.get_active_command_data(sos.user_id)

    return render_template(
        "sos/active.html",
        sos=sos,
        user=user,
        guidance_steps=command_data["guidance_steps"],
        trusted_contacts=command_data["trusted_contacts"],
        nearby_resources=command_data["nearby_resources"],
        disclaimer=Config.DISCLAIMER_TEXT
    )

@sos_bp.route("/resolve/<int:sos_id>", methods=["POST"])
@login_required
def resolve(sos_id: int):
    user = get_current_user()
    sos = SOSRepository.get_by_id(sos_id)

    if not sos or (sos.user_id != user.id and not user.is_admin):
        flash("Emergency alert not found.", "warning")
        return redirect(url_for("sos.center"))

    resolution_notes = request.form.get("resolution_notes", "Safety restored. User confirmed safe.").strip()
    resolved_by = "ADMIN" if user.is_admin and user.id != sos.user_id else "USER"
    ip_address = request.remote_addr or ""

    SOSService.resolve_sos(
        sos_id=sos.id,
        actor_email=user.email,
        resolved_by=resolved_by,
        resolution_notes=resolution_notes,
        ip_address=ip_address
    )

    flash("SOS event resolved successfully. We are glad you are safe.", "success")
    return redirect(url_for("sos.history"))

@sos_bp.route("/cancel/<int:sos_id>", methods=["POST"])
@login_required
def cancel(sos_id: int):
    user = get_current_user()
    sos = SOSRepository.get_by_id(sos_id)

    if not sos or (sos.user_id != user.id and not user.is_admin):
        flash("Emergency alert not found.", "warning")
        return redirect(url_for("sos.center"))

    reason = request.form.get("cancel_reason", "False alarm - triggered accidentally.").strip()
    cancelled_by = "ADMIN" if user.is_admin and user.id != sos.user_id else "USER"
    ip_address = request.remote_addr or ""

    SOSService.cancel_sos(
        sos_id=sos.id,
        actor_email=user.email,
        cancelled_by=cancelled_by,
        cancel_reason=reason,
        ip_address=ip_address
    )

    flash("SOS alert cancelled.", "info")
    return redirect(url_for("sos.history"))

@sos_bp.route("/history")
@login_required
def history():
    user = get_current_user()
    page = request.args.get("page", 1, type=int)
    per_page = 10

    events, total = SOSRepository.get_user_history(user.id, page=page, per_page=per_page)

    return render_template(
        "sos/history.html",
        events=events,
        total=total,
        page=page,
        per_page=per_page,
        disclaimer=Config.DISCLAIMER_TEXT
    )
