import os
from flask import Flask, render_template, session, jsonify, request
from app.config import config_by_name
from app.database import init_db
from app.security.csrf import init_csrf
from app.security.auth_decorators import get_current_user
from app.routes import register_blueprints
from app.repositories.notification_repo import NotificationRepository
from app.repositories.sos_repo import SOSRepository

def create_app(config_name: str = None) -> Flask:
    if not config_name:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Ensure instance directory exists
    instance_dir = os.path.join(app.root_path, "..", "instance")
    os.makedirs(instance_dir, exist_ok=True)

    # Initialize Database
    init_db(app)

    # Initialize Security & CSRF
    init_csrf(app)

    # Register Blueprints
    register_blueprints(app)

    # Global Template Context Processor
    @app.context_processor
    def inject_global_vars():
        user = get_current_user()
        unread_count = 0
        user_active_sos = None
        if user:
            try:
                unread_count = NotificationRepository.get_unread_count(user.id)
                user_active_sos = SOSRepository.get_active_for_user(user.id)
            except Exception:
                pass

        return dict(
            current_user=user,
            unread_notifications_count=unread_count,
            user_active_sos=user_active_sos,
            app_name=app.config.get("APP_NAME", "Women Safety Platform"),
            app_tagline=app.config.get("APP_TAGLINE", "Preparedness, Community Care & Rapid Assistance"),
            disclaimer_text=app.config.get("DISCLAIMER_TEXT"),
            readiness_disclaimer=app.config.get("READINESS_DISCLAIMER")
        )

    # Custom Error Handlers
    @app.errorhandler(400)
    def bad_request_error(e):
        if request.is_json or request.path.startswith("/api/"):
            return jsonify({"error": "Bad Request", "message": str(e)}), 400
        return render_template("errors/400.html", error=e), 400

    @app.errorhandler(401)
    def unauthorized_error(e):
        if request.is_json or request.path.startswith("/api/"):
            return jsonify({"error": "Unauthorized", "message": "Authentication required."}), 401
        return render_template("errors/401.html", error=e), 401

    @app.errorhandler(403)
    def forbidden_error(e):
        if request.is_json or request.path.startswith("/api/"):
            return jsonify({"error": "Forbidden", "message": "Access denied."}), 403
        return render_template("errors/403.html", error=e), 403

    @app.errorhandler(404)
    def not_found_error(e):
        if request.is_json or request.path.startswith("/api/"):
            return jsonify({"error": "Not Found", "message": "Resource not found."}), 404
        return render_template("errors/404.html", error=e), 404

    @app.errorhandler(405)
    def method_not_allowed_error(e):
        if request.is_json or request.path.startswith("/api/"):
            return jsonify({"error": "Method Not Allowed", "message": "HTTP method not allowed."}), 405
        return render_template("errors/405.html", error=e), 405

    @app.errorhandler(500)
    def internal_server_error(e):
        if request.is_json or request.path.startswith("/api/"):
            return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred."}), 500
        return render_template("errors/500.html", error=e), 500

    return app
