from flask import Blueprint, render_template, request, jsonify, session
from app.repositories.tip_repo import TipRepository
from app.security.auth_decorators import login_required, get_current_user
from app.validators.forms import TIP_CATEGORIES

tips_bp = Blueprint("tips", __name__, url_prefix="/tips")

@tips_bp.route("/")
def index():
    user = get_current_user()
    search = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()

    tips = TipRepository.get_published_tips(search=search, category=category, limit=50)
    viewed_ids = TipRepository.get_user_viewed_tip_ids(user.id) if user else set()

    return render_template(
        "tips/index.html",
        tips=tips,
        categories=TIP_CATEGORIES,
        selected_category=category,
        search=search,
        viewed_ids=viewed_ids
    )

@tips_bp.route("/<int:tip_id>")
def detail(tip_id: int):
    user = get_current_user()
    tip = TipRepository.get_by_id(tip_id)

    if not tip or not tip.is_published:
        flash("Safety guide not found.", "warning")
        return redirect(url_for("tips.index"))

    is_viewed = False
    if user:
        # Mark tip as viewed by this user
        is_viewed = TipRepository.record_view(user.id, tip.id)

    return render_template("tips/detail.html", tip=tip, is_viewed=is_viewed)

@tips_bp.route("/mark-viewed/<int:tip_id>", methods=["POST"])
@login_required
def mark_viewed(tip_id: int):
    user = get_current_user()
    tip = TipRepository.get_by_id(tip_id)
    if not tip:
        return jsonify({"success": False, "message": "Tip not found."}), 404

    recorded = TipRepository.record_view(user.id, tip.id)
    return jsonify({"success": True, "recorded": recorded})
