from flask import Blueprint, jsonify, request
from app.security.auth_decorators import get_current_user
from app.repositories.sos_repo import SOSRepository
from app.repositories.notification_repo import NotificationRepository
from app.repositories.resource_repo import ResourceRepository
from app.services.readiness_service import ReadinessService

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/sos/status")
def sos_status():
    user = get_current_user()
    if not user:
        return jsonify({"has_active_sos": False})

    active = SOSRepository.get_active_for_user(user.id)
    return jsonify({
        "has_active_sos": bool(active),
        "sos_id": active.id if active else None,
        "triggered_at": active.created_at.isoformat() if active else None
    })

@api_bp.route("/notifications/unread-count")
def unread_notifications():
    user = get_current_user()
    if not user:
        return jsonify({"count": 0})
    count = NotificationRepository.get_unread_count(user.id)
    return jsonify({"count": count})

@api_bp.route("/readiness")
def readiness():
    user = get_current_user()
    if not user:
        return jsonify({"score": 0})
    return jsonify(ReadinessService.calculate_score(user.id))

@api_bp.route("/resources")
def resources():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    city = request.args.get("city", "").strip()
    res = ResourceRepository.get_active_resources(search=q, category=category, city=city, limit=20)
    return jsonify([r.to_dict() for r in res])
