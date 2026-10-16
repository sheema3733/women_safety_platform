from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.security.auth_decorators import login_required, get_current_user
from app.repositories.contact_repo import ContactRepository
from app.repositories.user_repo import UserRepository
from app.validators.forms import validate_emergency_contact, ValidationError

contacts_bp = Blueprint("contacts", __name__, url_prefix="/contacts")

@contacts_bp.route("/")
@login_required
def index():
    user = get_current_user()
    search = request.args.get("q", "").strip().lower()
    contacts = ContactRepository.get_for_user(user.id)

    if search:
        contacts = [
            c for c in contacts
            if search in c.name.lower() or search in c.relationship.lower() or search in c.phone
        ]

    return render_template("contacts/index.html", contacts=contacts, search=search)

@contacts_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    user = get_current_user()
    errors = {}
    form_data = {}

    if request.method == "POST":
        form_data = request.form.to_dict()
        try:
            validated = validate_emergency_contact(form_data)
            contact = ContactRepository.create_contact(
                user_id=user.id,
                name=validated["name"],
                relationship=validated["relationship"],
                phone=validated["phone"],
                is_trusted=validated["is_trusted"],
                priority_order=validated["priority_order"]
            )
            UserRepository.log_activity(
                user_id=user.id,
                action="Contact Added",
                details=f"Added emergency contact: {contact.name} ({contact.relationship})",
                ip_address=request.remote_addr or ""
            )
            flash(f"Emergency contact '{contact.name}' added successfully.", "success")
            return redirect(url_for("contacts.index"))
        except ValidationError as ve:
            errors = ve.errors

    return render_template("contacts/form.html", errors=errors, form_data=form_data, is_edit=False)

@contacts_bp.route("/edit/<int:contact_id>", methods=["GET", "POST"])
@login_required
def edit(contact_id: int):
    user = get_current_user()
    contact = ContactRepository.get_by_id(contact_id)

    if not contact or contact.user_id != user.id:
        flash("Contact not found or access denied.", "danger")
        return redirect(url_for("contacts.index"))

    errors = {}
    form_data = {
        "name": contact.name,
        "relationship": contact.relationship,
        "phone": contact.phone,
        "is_trusted": contact.is_trusted,
        "priority_order": contact.priority_order
    }

    if request.method == "POST":
        form_data = request.form.to_dict()
        try:
            validated = validate_emergency_contact(form_data)
            ContactRepository.update_contact(
                contact=contact,
                name=validated["name"],
                relationship=validated["relationship"],
                phone=validated["phone"],
                is_trusted=validated["is_trusted"],
                priority_order=validated["priority_order"]
            )
            UserRepository.log_activity(
                user_id=user.id,
                action="Contact Updated",
                details=f"Updated contact: {contact.name}",
                ip_address=request.remote_addr or ""
            )
            flash("Contact updated successfully.", "success")
            return redirect(url_for("contacts.index"))
        except ValidationError as ve:
            errors = ve.errors

    return render_template("contacts/form.html", errors=errors, form_data=form_data, contact=contact, is_edit=True)

@contacts_bp.route("/delete/<int:contact_id>", methods=["POST"])
@login_required
def delete(contact_id: int):
    user = get_current_user()
    contact = ContactRepository.get_by_id(contact_id)

    if contact and contact.user_id == user.id:
        name = contact.name
        ContactRepository.delete_contact(contact)
        UserRepository.log_activity(
            user_id=user.id,
            action="Contact Deleted",
            details=f"Deleted contact: {name}",
            ip_address=request.remote_addr or ""
        )
        flash(f"Contact '{name}' removed.", "info")
    else:
        flash("Contact not found.", "warning")

    return redirect(url_for("contacts.index"))

@contacts_bp.route("/toggle-trusted/<int:contact_id>", methods=["POST"])
@login_required
def toggle_trusted(contact_id: int):
    user = get_current_user()
    contact = ContactRepository.get_by_id(contact_id)

    if not contact or contact.user_id != user.id:
        return jsonify({"success": False, "message": "Contact not found."}), 404

    new_val = not contact.is_trusted
    ContactRepository.update_contact(contact, is_trusted=new_val)
    return jsonify({"success": True, "is_trusted": new_val})
