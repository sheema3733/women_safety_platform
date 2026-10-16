from flask import Blueprint, jsonify, request
from app.security.auth_decorators import get_current_user
from app.repositories.sos_repo import SOSRepository
from app.repositories.notification_repo import NotificationRepository
from app.repositories.resource_repo import ResourceRepository
from app.services.readiness_service import ReadinessService
from app.services.sos_service import SOSService
from app.validators.forms import validate_coordinates

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/sos/status")
def sos_status():
    user = get_current_user()
    if not user:
        return jsonify({"has_active_sos": False, "authenticated": False}), 200

    active = SOSRepository.get_active_for_user(user.id)
    return jsonify({
        "has_active_sos": bool(active),
        "sos_id": active.id if active else None,
        "triggered_at": active.created_at.isoformat() if active else None,
        "status": active.status if active else None,
        "authenticated": True
    }), 200

@api_bp.route("/sos/active")
def sos_active_details():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Authentication required to access active SOS command telemetry.", "status_code": 401}), 401

    active = SOSRepository.get_active_for_user(user.id)
    if not active:
        return jsonify({"error": "No active emergency SOS session found for user.", "has_active_sos": False}), 404

    command_data = SOSService.get_active_command_data(user.id)
    return jsonify({
        "sos_id": active.id,
        "status": active.status,
        "trigger_type": active.trigger_type,
        "triggered_at": active.created_at.isoformat(),
        "latitude": active.latitude,
        "longitude": active.longitude,
        "address_note": active.address_note,
        "emergency_notes": active.emergency_notes,
        "guidance_steps": command_data.get("guidance_steps", []),
        "trusted_contacts_count": len(command_data.get("trusted_contacts", [])),
        "nearby_resources_count": len(command_data.get("nearby_resources", []))
    }), 200

@api_bp.route("/notifications/unread-count")
def unread_notifications():
    user = get_current_user()
    if not user:
        return jsonify({"count": 0, "authenticated": False}), 200
    count = NotificationRepository.get_unread_count(user.id)
    return jsonify({"count": count, "authenticated": True}), 200

@api_bp.route("/readiness")
def readiness():
    user = get_current_user()
    if not user:
        return jsonify({"score": 0, "authenticated": False}), 200
    data = ReadinessService.calculate_score(user.id)
    return jsonify(data), 200

@api_bp.route("/resources")
def resources():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    city = request.args.get("city", "").strip()
    
    # Validate limit parameter (1 to 100)
    limit_val = request.args.get("limit", 20)
    try:
        limit = int(limit_val)
        if limit < 1:
            limit = 20
        elif limit > 100:
            limit = 100
    except (ValueError, TypeError):
        limit = 20

    res = ResourceRepository.get_active_resources(search=q, category=category, city=city, limit=limit)
    return jsonify({
        "count": len(res),
        "limit": limit,
        "results": [r.to_dict() for r in res]
    }), 200

@api_bp.route("/resources/nearby")
def nearby_resources():
    lat = request.args.get("lat")
    lng = request.args.get("lng")
    category = request.args.get("category", "").strip()
    city = request.args.get("city", "").strip()

    # Validate coordinate parameters
    latitude, longitude, coord_err = validate_coordinates(lat, lng, required=True)
    if coord_err:
        return jsonify({"error": coord_err, "status_code": 400}), 400

    # Validate radius_km parameter (0.5 to 100.0 km)
    radius_val = request.args.get("radius_km", 10.0)
    try:
        radius_km = float(radius_val)
        if radius_km < 0.5:
            radius_km = 0.5
        elif radius_km > 100.0:
            radius_km = 100.0
    except (ValueError, TypeError):
        radius_km = 10.0

    # Validate limit parameter (1 to 50)
    limit_val = request.args.get("limit", 20)
    try:
        limit = int(limit_val)
        if limit < 1:
            limit = 20
        elif limit > 50:
            limit = 50
    except (ValueError, TypeError):
        limit = 20

    nearby = ResourceRepository.get_nearby_resources(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        category=category,
        city=city,
        limit=limit
    )

    results = []
    for resource, dist_km in nearby:
        item = resource.to_dict()
        item["distance_km"] = dist_km
        results.append(item)

    return jsonify({
        "query_coordinates": {"latitude": latitude, "longitude": longitude},
        "radius_km": radius_km,
        "count": len(results),
        "results": results
    }), 200
