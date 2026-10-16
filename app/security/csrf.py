import secrets
from flask import session, request, abort, current_app

def generate_csrf_token() -> str:
    """Generate or retrieve a CSRF token for the current session."""
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]

def validate_csrf_token(token: str) -> bool:
    """Validate submitted token against session token."""
    stored_token = session.get("_csrf_token")
    if not stored_token or not token:
        return False
    return secrets.compare_digest(stored_token, token)

def init_csrf(app):
    """Register CSRF protection middleware and Jinja helper."""
    @app.before_request
    def check_csrf():
        # Allow disabling CSRF in testing environment
        if app.config.get("TESTING") and not app.config.get("WTF_CSRF_ENABLED", False):
            return

        if request.method in ("POST", "PUT", "DELETE", "PATCH"):
            # Check JSON header or form data or custom header
            token = (
                request.form.get("csrf_token")
                or request.headers.get("X-CSRF-Token")
                or (request.is_json and request.get_json(silent=True) and request.get_json(silent=True).get("csrf_token"))
            )
            if not token or not validate_csrf_token(token):
                # If API call, return 400 with message, else abort(400)
                abort(400, description="Invalid or missing CSRF token.")

    @app.context_processor
    def inject_csrf():
        return dict(csrf_token=generate_csrf_token)
