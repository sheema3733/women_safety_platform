import re
from datetime import datetime

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\+?[0-9\s\-()]{7,25}$")

INCIDENT_TYPES = [
    "Harassment",
    "Suspicious Activity",
    "Unsafe Transportation",
    "Online Harassment",
    "Public Place Safety Issue",
    "Other"
]

RESOURCE_CATEGORIES = [
    "Police Station",
    "Hospital",
    "Women’s Support Center",
    "Safe Place",
    "Emergency Support Center"
]

TIP_CATEGORIES = [
    "Travel Safety",
    "Public Transport",
    "Online Safety",
    "Workplace Safety",
    "College Safety",
    "Night Travel",
    "Emergency Preparedness",
    "Digital Privacy"
]

SEVERITIES = ["LOW", "MEDIUM", "HIGH"]
INCIDENT_STATUSES = ["SUBMITTED", "UNDER REVIEW", "RESOLVED", "CLOSED"]

class ValidationError(Exception):
    def __init__(self, errors: dict):
        super().__init__("Validation failed")
        self.errors = errors

def validate_registration(data: dict) -> dict:
    errors = {}
    email = (data.get("email") or "").strip().lower()
    full_name = (data.get("full_name") or "").strip()
    password = data.get("password") or ""
    confirm_password = data.get("confirm_password") or ""
    phone = (data.get("phone") or "").strip()
    city = (data.get("city") or "").strip()

    if not email:
        errors["email"] = "Email address is required."
    elif not EMAIL_REGEX.match(email):
        errors["email"] = "Please provide a valid email address."

    if not full_name:
        errors["full_name"] = "Full name is required."
    elif len(full_name) < 2 or len(full_name) > 100:
        errors["full_name"] = "Full name must be between 2 and 100 characters."

    if not password:
        errors["password"] = "Password is required."
    elif len(password) < 8:
        errors["password"] = "Password must be at least 8 characters long."
    elif not re.search(r"[A-Z]", password):
        errors["password"] = "Password must contain at least one uppercase letter."
    elif not re.search(r"[a-z]", password):
        errors["password"] = "Password must contain at least one lowercase letter."
    elif not re.search(r"[0-9]", password):
        errors["password"] = "Password must contain at least one number."

    if password and confirm_password and password != confirm_password:
        errors["confirm_password"] = "Passwords do not match."

    if phone and not PHONE_REGEX.match(phone):
        errors["phone"] = "Please enter a valid phone number."

    if city and len(city) > 100:
        errors["city"] = "City name cannot exceed 100 characters."

    if errors:
        raise ValidationError(errors)

    return {
        "email": email,
        "full_name": full_name,
        "password": password,
        "phone": phone,
        "city": city
    }

def validate_login(data: dict) -> dict:
    errors = {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email:
        errors["email"] = "Email address is required."
    if not password:
        errors["password"] = "Password is required."

    if errors:
        raise ValidationError(errors)

    return {"email": email, "password": password}

def validate_profile_update(data: dict) -> dict:
    errors = {}
    full_name = (data.get("full_name") or "").strip()
    phone = (data.get("phone") or "").strip()
    city = (data.get("city") or "").strip()

    if not full_name:
        errors["full_name"] = "Full name is required."
    elif len(full_name) < 2 or len(full_name) > 100:
        errors["full_name"] = "Full name must be between 2 and 100 characters."

    if phone and not PHONE_REGEX.match(phone):
        errors["phone"] = "Please enter a valid phone number."

    if city and len(city) > 100:
        errors["city"] = "City name cannot exceed 100 characters."

    if errors:
        raise ValidationError(errors)

    return {"full_name": full_name, "phone": phone, "city": city}

def validate_emergency_contact(data: dict) -> dict:
    errors = {}
    name = (data.get("name") or "").strip()
    relationship = (data.get("relationship") or "").strip()
    phone = (data.get("phone") or "").strip()
    is_trusted = bool(data.get("is_trusted") in (True, "true", "True", "1", 1, "on"))
    priority_order = data.get("priority_order", 1)

    if not name:
        errors["name"] = "Contact name is required."
    elif len(name) < 2 or len(name) > 100:
        errors["name"] = "Contact name must be between 2 and 100 characters."

    if not relationship:
        errors["relationship"] = "Relationship is required."

    if not phone:
        errors["phone"] = "Contact phone number is required."
    elif not PHONE_REGEX.match(phone):
        errors["phone"] = "Please enter a valid phone number."

    try:
        priority_order = int(priority_order)
        if priority_order < 1:
            priority_order = 1
    except (ValueError, TypeError):
        priority_order = 1

    if errors:
        raise ValidationError(errors)

    return {
        "name": name,
        "relationship": relationship,
        "phone": phone,
        "is_trusted": is_trusted,
        "priority_order": priority_order
    }

def validate_incident_report(data: dict) -> dict:
    errors = {}
    incident_type = (data.get("incident_type") or "").strip()
    general_area = (data.get("general_area") or "").strip()
    description = (data.get("description") or "").strip()
    severity = (data.get("severity") or "MEDIUM").strip().upper()
    date_str = (data.get("incident_date") or "").strip()

    if not incident_type:
        errors["incident_type"] = "Please select an incident type."
    elif incident_type not in INCIDENT_TYPES:
        errors["incident_type"] = "Invalid incident type selected."

    if not general_area:
        errors["general_area"] = "Location or general area is required."
    elif len(general_area) < 2 or len(general_area) > 150:
        errors["general_area"] = "Area must be between 2 and 150 characters."

    if not description:
        errors["description"] = "Incident description is required."
    elif len(description) < 10:
        errors["description"] = "Please provide more details (at least 10 characters)."

    if severity not in SEVERITIES:
        errors["severity"] = "Invalid severity level selected."

    incident_date = datetime.now()
    if date_str:
        try:
            # support ISO and date input
            if "T" in date_str:
                incident_date = datetime.fromisoformat(date_str)
            else:
                incident_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            errors["incident_date"] = "Please enter a valid date/time."

    if errors:
        raise ValidationError(errors)

    return {
        "incident_type": incident_type,
        "general_area": general_area,
        "description": description,
        "severity": severity,
        "incident_date": incident_date
    }

def validate_coordinates(lat_val, lng_val, required: bool = False) -> tuple:
    """
    Validates latitude and longitude values.
    Returns (latitude: float | None, longitude: float | None, error_message: str | None).
    """
    if lat_val is None or str(lat_val).strip() == "":
        if required:
            return None, None, "Latitude coordinate is required."
        lat = None
    else:
        try:
            lat = float(lat_val)
            if not (-90.0 <= lat <= 90.0):
                return None, None, "Latitude must be between -90.0 and 90.0 degrees."
        except (ValueError, TypeError):
            return None, None, "Latitude must be a valid decimal number."

    if lng_val is None or str(lng_val).strip() == "":
        if required:
            return None, None, "Longitude coordinate is required."
        lng = None
    else:
        try:
            lng = float(lng_val)
            if not (-180.0 <= lng <= 180.0):
                return None, None, "Longitude must be between -180.0 and 180.0 degrees."
        except (ValueError, TypeError):
            return None, None, "Longitude must be a valid decimal number."

    if (lat is not None and lng is None) or (lat is None and lng is not None):
        return None, None, "Both latitude and longitude must be provided together."

    return lat, lng, None

def validate_resource(data: dict) -> dict:
    errors = {}
    name = (data.get("name") or "").strip()
    category = (data.get("category") or "").strip()
    city = (data.get("city") or "").strip()
    general_area = (data.get("general_area") or "").strip()
    demo_phone = (data.get("demo_phone") or "").strip()
    description = (data.get("description") or "").strip()
    is_active = bool(data.get("is_active") in (True, "true", "True", "1", 1, "on"))
    lat = data.get("latitude")
    lng = data.get("longitude")

    if not name:
        errors["name"] = "Resource name is required."
    if not category or category not in RESOURCE_CATEGORIES:
        errors["category"] = "Please select a valid resource category."
    if not city:
        errors["city"] = "City is required."
    if not general_area:
        errors["general_area"] = "General area is required."
    if not demo_phone:
        errors["demo_phone"] = "Contact phone number is required."

    latitude, longitude, coord_err = validate_coordinates(lat, lng, required=False)
    if coord_err:
        errors["coordinates"] = coord_err

    if errors:
        raise ValidationError(errors)

    return {
        "name": name,
        "category": category,
        "city": city,
        "general_area": general_area,
        "demo_phone": demo_phone,
        "description": description,
        "latitude": latitude,
        "longitude": longitude,
        "is_active": is_active
    }

def validate_safety_tip(data: dict) -> dict:
    errors = {}
    title = (data.get("title") or "").strip()
    category = (data.get("category") or "").strip()
    summary = (data.get("summary") or "").strip()
    content = (data.get("content") or "").strip()
    read_time = data.get("read_time_minutes", 3)
    is_published = bool(data.get("is_published") in (True, "true", "True", "1", 1, "on"))

    if not title:
        errors["title"] = "Tip title is required."
    if not category or category not in TIP_CATEGORIES:
        errors["category"] = "Please select a valid category."
    if not summary:
        errors["summary"] = "Brief summary is required."
    if not content:
        errors["content"] = "Full tip content is required."

    try:
        read_time = int(read_time)
        if read_time < 1:
            read_time = 1
    except (ValueError, TypeError):
        read_time = 3

    if errors:
        raise ValidationError(errors)

    return {
        "title": title,
        "category": category,
        "summary": summary,
        "content": content,
        "read_time_minutes": read_time,
        "is_published": is_published
    }
