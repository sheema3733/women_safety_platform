from flask import Blueprint, render_template, request, flash
from app.repositories.resource_repo import ResourceRepository
from app.validators.forms import RESOURCE_CATEGORIES

resources_bp = Blueprint("resources", __name__, url_prefix="/resources")

@resources_bp.route("/")
def index():
    search = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    city = request.args.get("city", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 12

    resources, total = ResourceRepository.list_all_resources(
        search=search,
        category=category,
        city=city,
        status_filter="active",
        page=page,
        per_page=per_page
    )

    cities = ResourceRepository.get_distinct_cities()

    return render_template(
        "resources/index.html",
        resources=resources,
        total=total,
        page=page,
        per_page=per_page,
        search=search,
        selected_category=category,
        selected_city=city,
        categories=RESOURCE_CATEGORIES,
        cities=cities
    )

@resources_bp.route("/<int:resource_id>")
def detail(resource_id: int):
    resource = ResourceRepository.get_by_id(resource_id)
    if not resource or not resource.is_active:
        flash("Emergency resource not found.", "warning")
        return redirect(url_for("resources.index"))

    return render_template("resources/detail.html", resource=resource)
