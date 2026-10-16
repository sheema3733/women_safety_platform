from flask import Blueprint, render_template, request, jsonify
from app.security.auth_decorators import login_required, get_current_user
from app.repositories.checklist_repo import ChecklistRepository
from app.repositories.user_repo import UserRepository
from app.services.readiness_service import ReadinessService
from app.config import Config

checklist_bp = Blueprint("checklist", __name__, url_prefix="/checklist")

@checklist_bp.route("/")
@login_required
def index():
    user = get_current_user()
    items = ChecklistRepository.get_all_items()
    user_progress = ChecklistRepository.get_user_progress(user.id)
    stats = ChecklistRepository.get_user_stats(user.id)
    readiness = ReadinessService.calculate_score(user.id)

    return render_template(
        "checklist/index.html",
        items=items,
        user_progress=user_progress,
        stats=stats,
        readiness=readiness,
        disclaimer=Config.READINESS_DISCLAIMER
    )

@checklist_bp.route("/toggle/<int:item_id>", methods=["POST"])
@login_required
def toggle(item_id: int):
    user = get_current_user()
    item = ChecklistRepository.get_by_id(item_id)
    if not item:
        return jsonify({"success": False, "message": "Item not found."}), 404

    data = request.get_json(silent=True) or request.form
    is_completed = bool(data.get("is_completed") in (True, "true", "True", "1", 1))

    ChecklistRepository.toggle_item(user.id, item_id, is_completed)
    stats = ChecklistRepository.get_user_stats(user.id)
    readiness = ReadinessService.calculate_score(user.id)

    UserRepository.log_activity(
        user_id=user.id,
        action="Checklist Updated",
        details=f"Item '{item.title}' marked as {'completed' if is_completed else 'incomplete'}",
        ip_address=request.remote_addr or ""
    )

    return jsonify({
        "success": True,
        "is_completed": is_completed,
        "stats": stats,
        "readiness_score": readiness["score"]
    })
