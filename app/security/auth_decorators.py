from functools import wraps
from flask import session, redirect, url_for, request, abort, jsonify
from app.database import db_session
from app.models.user import User

def get_current_user():
    """Retrieve current authenticated User model from database or None."""
    user_id = session.get("user_id")
    if not user_id or not db_session:
        return None
    return db_session.get(User, user_id)

def login_required(f):
    """Decorator requiring a user to be logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"success": False, "message": "Authentication required."}), 401
            return redirect(url_for("auth.login", next=request.url))
        
        # Verify user still exists and is active
        user = get_current_user()
        if not user or not user.is_active:
            session.clear()
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"success": False, "message": "Account is inactive or disabled."}), 403
            return redirect(url_for("auth.login", error="Your account has been deactivated."))
            
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """Decorator requiring the logged-in user to have a specific role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                if request.is_json or request.path.startswith("/api/"):
                    return jsonify({"success": False, "message": "Authentication required."}), 401
                return redirect(url_for("auth.login", next=request.url))

            user_role = session.get("user_role")
            if not user_role or user_role not in roles:
                if request.is_json or request.path.startswith("/api/"):
                    return jsonify({"success": False, "message": "Access denied. Insufficient permissions."}), 403
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def anonymous_required(f):
    """Decorator restricting authenticated users from visiting login/register."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" in session:
            if session.get("user_role") == "ADMIN":
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("user.dashboard"))
        return f(*args, **kwargs)
    return decorated_function
