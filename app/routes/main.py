from flask import Blueprint, render_template, request
from app.repositories.resource_repo import ResourceRepository
from app.repositories.tip_repo import TipRepository

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    featured_tips = TipRepository.get_published_tips(limit=3)
    sample_resources = ResourceRepository.get_active_resources(limit=4)
    return render_template("landing.html", featured_tips=featured_tips, sample_resources=sample_resources)

@main_bp.route("/about")
def about():
    return render_template("about.html")

@main_bp.route("/disclaimer")
def disclaimer():
    return render_template("disclaimer.html")
