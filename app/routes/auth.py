from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.auth_service import AuthService
from app.validators.forms import validate_registration, validate_login, ValidationError
from app.security.auth_decorators import anonymous_required, login_required

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
@anonymous_required
def register():
    errors = {}
    form_data = {}
    if request.method == "POST":
        form_data = request.form.to_dict()
        try:
            validated = validate_registration(form_data)
            ip_address = request.remote_addr or ""
            user, err_msg = AuthService.register_user(validated, ip_address=ip_address)
            if err_msg:
                errors["general"] = err_msg
            else:
                AuthService.start_session(user)
                flash("Registration successful! Welcome to your safety platform.", "success")
                return redirect(url_for("user.dashboard"))
        except ValidationError as ve:
            errors = ve.errors

    return render_template("auth/register.html", errors=errors, form_data=form_data)

@auth_bp.route("/login", methods=["GET", "POST"])
@anonymous_required
def login():
    errors = {}
    form_data = {}
    if request.method == "POST":
        form_data = request.form.to_dict()
        try:
            validated = validate_login(form_data)
            ip_address = request.remote_addr or ""
            user, err_msg = AuthService.authenticate_user(
                email=validated["email"],
                password=validated["password"],
                ip_address=ip_address
            )
            if err_msg:
                errors["general"] = err_msg
            else:
                AuthService.start_session(user)
                flash(f"Welcome back, {user.full_name}!", "success")
                next_url = request.args.get("next")
                if next_url and not next_url.startswith("//") and not next_url.startswith("http"):
                    return redirect(next_url)
                if user.is_admin:
                    return redirect(url_for("admin.dashboard"))
                return redirect(url_for("user.dashboard"))
        except ValidationError as ve:
            errors = ve.errors

    return render_template("auth/login.html", errors=errors, form_data=form_data)

@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    user_id = session.get("user_id")
    ip_address = request.remote_addr or ""
    AuthService.end_session(user_id=user_id, ip_address=ip_address)
    flash("You have been safely logged out.", "info")
    return redirect(url_for("auth.login"))
