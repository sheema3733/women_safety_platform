from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.security.auth_decorators import login_required, get_current_user
from app.repositories.notification_repo import NotificationRepository

notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")

@notifications_bp.route("/")
@login_required
def index():
    user = get_current_user()
    page = request.args.get("page", 1, type=int)
    unread_only = request.args.get("unread", "false").lower() == "true"
    per_page = 15

    notifications, total = NotificationRepository.get_for_user(
        user_id=user.id,
        page=page,
        per_page=per_page,
        unread_only=unread_only
    )
    unread_count = NotificationRepository.get_unread_count(user.id)

    return render_template(
        "notifications/index.html",
        notifications=notifications,
        total=total,
        page=page,
        per_page=per_page,
        unread_only=unread_only,
        unread_count=unread_count
    )

@notifications_bp.route("/read/<int:notification_id>", methods=["POST"])
@login_required
def mark_read(notification_id: int):
    user = get_current_user()
    success = NotificationRepository.mark_as_read(notification_id, user.id)
    if request.is_json:
        return jsonify({"success": success})
    return redirect(url_for("notifications.index"))

@notifications_bp.route("/read-all", methods=["POST"])
@login_required
def mark_all_read():
    user = get_current_user()
    count = NotificationRepository.mark_all_as_read(user.id)
    flash(f"Marked {count} notifications as read.", "info")
    if request.is_json:
        return jsonify({"success": True, "count": count})
    return redirect(url_for("notifications.index"))
