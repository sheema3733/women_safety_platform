import os
import sys
from datetime import datetime, timedelta, timezone

# Add project root to sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app import create_app
from app.database import create_all_tables, db_session
from app.models.user import Role, User, UserActivity
from app.models.contact import EmergencyContact
from app.models.sos import SOSEvent, SOSAuditLog
from app.models.incident import IncidentReport, IncidentTimeline
from app.models.resource import EmergencyResource
from app.models.tip import SafetyTip, TipView
from app.models.checklist import ChecklistItem, UserChecklistProgress
from app.models.notification import Notification
from app.models.audit import AuditLog
from app.models.settings import SystemSetting
from app.security.hashing import hash_password

def seed_database():
    app = create_app("development")
    with app.app_context():
        print("[*] Initializing database schema...")
        create_all_tables()

        # 1. Roles
        print("[+] Creating user roles...")
        user_role = db_session.query(Role).filter_by(name="USER").first()
        if not user_role:
            user_role = Role(name="USER", description="Standard Platform User")
            db_session.add(user_role)

        admin_role = db_session.query(Role).filter_by(name="ADMIN").first()
        if not admin_role:
            admin_role = Role(name="ADMIN", description="Platform Administrator with Full Access")
            db_session.add(admin_role)

        db_session.commit()

        # 2. Demo Users
        print("[+] Seeding demo users...")
        admin = db_session.query(User).filter_by(email="admin@womensafety.org").first()
        if not admin:
            admin = User(
                email="admin@womensafety.org",
                password_hash=hash_password("Admin@12345"),
                full_name="Sarah Jenkins (Admin)",
                phone="+1 555-0100",
                city="Central Metropolitan",
                role_id=admin_role.id,
                is_active=True
            )
            db_session.add(admin)

        user = db_session.query(User).filter_by(email="user@womensafety.org").first()
        if not user:
            user = User(
                email="user@womensafety.org",
                password_hash=hash_password("User@12345"),
                full_name="Elena Rostova",
                phone="+1 555-0199",
                city="Central Metropolitan",
                role_id=user_role.id,
                is_active=True
            )
            db_session.add(user)

        db_session.commit()

        # 3. Emergency Contacts for Demo User
        print("[+] Seeding emergency contacts...")
        if not db_session.query(EmergencyContact).filter_by(user_id=user.id).first():
            contacts = [
                EmergencyContact(
                    user_id=user.id,
                    name="Maria Rostova",
                    relationship="Sister",
                    phone="+1 555-0122",
                    is_trusted=True,
                    priority_order=1
                ),
                EmergencyContact(
                    user_id=user.id,
                    name="David Chen",
                    relationship="Partner",
                    phone="+1 555-0144",
                    is_trusted=True,
                    priority_order=2
                ),
                EmergencyContact(
                    user_id=user.id,
                    name="Aisha Patel",
                    relationship="Close Friend / Roommate",
                    phone="+1 555-0188",
                    is_trusted=False,
                    priority_order=3
                )
            ]
            db_session.add_all(contacts)
            db_session.commit()

        # 4. Emergency Resources
        print("[+] Seeding verified emergency resources...")
        if db_session.query(EmergencyResource).count() == 0:
            resources = [
                EmergencyResource(
                    name="Central Women & Children Special Police Station",
                    category="Police Station",
                    city="Central Metropolitan",
                    general_area="Civic Center, Block 4",
                    demo_phone="1091",
                    description="24/7 dedicated women safety police division with immediate mobile response patrol units.",
                    latitude=40.7128,
                    longitude=-74.0060,
                    is_active=True
                ),
                EmergencyResource(
                    name="Metro General Hospital Emergency Trauma Center",
                    category="Hospital",
                    city="Central Metropolitan",
                    general_area="Eastside Medical District",
                    demo_phone="911",
                    description="Level 1 emergency medical trauma center with forensic medical examination and trauma counseling.",
                    latitude=40.7306,
                    longitude=-73.9352,
                    is_active=True
                ),
                EmergencyResource(
                    name="Hope Haven Women’s Crisis Support Center",
                    category="Women’s Support Center",
                    city="Central Metropolitan",
                    general_area="West End Community Hub",
                    demo_phone="+1 800-799-7233",
                    description="Confidential emergency shelter, legal counseling, psychologist support, and crisis intervention.",
                    latitude=40.7580,
                    longitude=-73.9855,
                    is_active=True
                ),
                EmergencyResource(
                    name="Downtown Transit Safe Haven Desk",
                    category="Safe Place",
                    city="Central Metropolitan",
                    general_area="Grand Station Concourse Level B",
                    demo_phone="+1 555-0111",
                    description="Staffed safety outpost with security cameras, direct emergency telephone, and first-aid personnel.",
                    latitude=40.7527,
                    longitude=-73.9772,
                    is_active=True
                ),
                EmergencyResource(
                    name="Citywide 24/7 Emergency Support Coordination Center",
                    category="Emergency Support Center",
                    city="Central Metropolitan",
                    general_area="Northside Municipal Complex",
                    demo_phone="112",
                    description="Inter-agency rapid dispatch center coordinating police, paramedics, and mental health crisis workers.",
                    latitude=40.7831,
                    longitude=-73.9712,
                    is_active=True
                ),
                EmergencyResource(
                    name="South Suburban Police Station & Women Desk",
                    category="Police Station",
                    city="Central Metropolitan",
                    general_area="Southpark District",
                    demo_phone="+1 555-0155",
                    description="Suburban precinct with trained female officers available 24 hours a day.",
                    latitude=40.6782,
                    longitude=-73.9442,
                    is_active=True
                )
            ]
            db_session.add_all(resources)
            db_session.commit()

        # 5. Safety Tips (Across all 8 domains)
        print("[+] Seeding comprehensive safety guides...")
        if db_session.query(SafetyTip).count() == 0:
            tips = [
                SafetyTip(
                    title="Navigating Public Transit with Confidence and Alertness",
                    category="Public Transport",
                    summary="Strategic seating choices, situational awareness, and transit app features to safeguard late journeys.",
                    content=(
                        "When using buses, trams, or commuter trains, sit near the driver, operator, or conductor whenever possible. "
                        "Avoid empty train carriages, especially on late-night routes. Keep your mobile phone charged and easily accessible "
                        "rather than buried inside a deep backpack. If someone makes you uncomfortable, do not hesitate to change seats or carriages immediately."
                    ),
                    read_time_minutes=4,
                    is_published=True,
                    view_count=18
                ),
                SafetyTip(
                    title="Essential Precautions for Night Walking and Solo Travel",
                    category="Night Travel",
                    summary="Route planning, lighting observation, and body language techniques that deter unwanted approaches.",
                    content=(
                        "Walk with purpose and assertive posture. Keep both ears free of noise-canceling headphones so you can remain aware "
                        "of footsteps and vehicle sounds behind you. Stick to well-illuminated main thoroughfares, avoiding unlit alleys or desolate park shortcuts. "
                        "Share your estimated time of arrival with a trusted contact before embarking."
                    ),
                    read_time_minutes=3,
                    is_published=True,
                    view_count=24
                ),
                SafetyTip(
                    title="Digital Privacy: Hardening Location Sharing and Social Metadata",
                    category="Digital Privacy",
                    summary="How to prevent unintentional location tracking across check-ins, geotags, and public sharing apps.",
                    content=(
                        "Review app permissions on your mobile device regularly. Disable persistent 'Always Allow' location permissions for non-essential apps. "
                        "Never post real-time check-ins from your home, school, or daily fitness routes; wait until you have departed a venue before sharing photos. "
                        "Ensure your profile privacy settings on mainstream social media are restricted to verified connections."
                    ),
                    read_time_minutes=5,
                    is_published=True,
                    view_count=31
                ),
                SafetyTip(
                    title="Rideshare & Taxi Safety: The 4-Point Verification Checklist",
                    category="Travel Safety",
                    summary="Crucial steps before entering any rideshare vehicle, including license plate confirmation and child-lock checks.",
                    content=(
                        "1. Verify license plate, vehicle make/model, and driver photograph before opening the car door.\n"
                        "2. Ask the driver 'Who are you here to pick up?' rather than stating your name first.\n"
                        "3. Sit in the back seat on the passenger side to maximize distance from the driver and allow egress from either side.\n"
                        "4. Share your live trip status with a trusted emergency contact via your preferred navigation application."
                    ),
                    read_time_minutes=3,
                    is_published=True,
                    view_count=42
                ),
                SafetyTip(
                    title="Workplace Harassment: Documentation and Secure Action Steps",
                    category="Workplace Safety",
                    summary="Establishing verifiable paper trails, boundary setting, and formal reporting channels for workplace security.",
                    content=(
                        "Document every incident contemporaneously: write down the exact date, time, location, persons present, and specific verbal or physical actions. "
                        "Store these records on a personal, non-work device. Familiarize yourself with internal HR grievance policies and seek independent advice "
                        "from verified worker support organizations if internal procedures are inadequate."
                    ),
                    read_time_minutes=4,
                    is_published=True,
                    view_count=15
                ),
                SafetyTip(
                    title="Campus Safety: Dormitory Security and Late Study Transitions",
                    category="College Safety",
                    summary="Safety escorts, blue-light stations, and safe study habits for university students.",
                    content=(
                        "Save the campus public safety dispatch phone number as a speed-dial contact. When studying late in libraries or research labs, "
                        "request an official campus security walking escort to your vehicle or dorm. Never prop exterior dormitory entrance doors open."
                    ),
                    read_time_minutes=3,
                    is_published=True,
                    view_count=12
                ),
                SafetyTip(
                    title="Building a Personal Emergency Action & Evacuation Kit",
                    category="Emergency Preparedness",
                    summary="Physical essentials, backup power, copy of key documents, and personal defense awareness.",
                    content=(
                        "Assemble a compact go-bag containing an external power bank with charging cable, a loud whistle, personal medical items, "
                        "a printed list of emergency phone numbers, a mini flashlight, and a modest amount of cash. Keep this kit in a known, accessible place."
                    ),
                    read_time_minutes=4,
                    is_published=True,
                    view_count=20
                ),
                SafetyTip(
                    title="Recognizing and Combating Online Harassment and Cyberstalking",
                    category="Online Safety",
                    summary="Handling aggressive trolling, doxxing threats, and collecting digital evidence safely.",
                    content=(
                        "Take clear screenshots of threatening messages, including date stamps, sender handles, and profile URLs before blocking. "
                        "Do not engage or respond to perpetrators, as engagement often escalates harassment. Report abusive behavior directly to platform trust teams "
                        "and consult cyber-safety hotlines."
                    ),
                    read_time_minutes=4,
                    is_published=True,
                    view_count=19
                )
            ]
            db_session.add_all(tips)
            db_session.commit()

        # 6. Safety Checklist Items
        print("[+] Seeding safety checklist items...")
        if db_session.query(ChecklistItem).count() == 0:
            checklist_items = [
                ChecklistItem(
                    title="Configure At Least 2 Emergency Contacts",
                    description="Designate family members or close friends with phone numbers verified for instant contact.",
                    category="Communication",
                    sort_order=1
                ),
                ChecklistItem(
                    title="Designate At Least 1 Trusted Contact",
                    description="Ensure your primary responder is marked as 'Trusted' for priority one-touch dialing in SOS.",
                    category="Communication",
                    sort_order=2
                ),
                ChecklistItem(
                    title="Save Local Emergency Hotlines in Your Phone",
                    description="Store police (1091/112/911), local transit safety lines, and national women helplines.",
                    category="Contacts",
                    sort_order=3
                ),
                ChecklistItem(
                    title="Locate Nearest Verified Safe Haven & Hospital",
                    description="Identify the nearest 24/7 hospital emergency center and police station along your daily route.",
                    category="Preparedness",
                    sort_order=4
                ),
                ChecklistItem(
                    title="Complete Profile Details (City & Phone)",
                    description="Ensure your city and primary contact number are up-to-date in your platform profile.",
                    category="Profile",
                    sort_order=5
                ),
                ChecklistItem(
                    title="Read 'Rideshare & Taxi Safety' Protocol",
                    description="Review the 4-point verification checklist before booking next transit trip.",
                    category="Education",
                    sort_order=6
                )
            ]
            db_session.add_all(checklist_items)
            db_session.commit()

            # Seed demo user progress for first 3 items
            for i, item in enumerate(checklist_items[:3]):
                db_session.add(UserChecklistProgress(
                    user_id=user.id,
                    item_id=item.id,
                    is_completed=True,
                    completed_at=datetime.now(timezone.utc)
                ))
            db_session.commit()

        # 7. Seed Sample Incidents for Analytics & Admin Review
        print("[+] Seeding sample incident reports...")
        if db_session.query(IncidentReport).count() == 0:
            sample_incidents = [
                IncidentReport(
                    user_id=user.id,
                    incident_type="Harassment",
                    incident_date=datetime.now() - timedelta(days=2),
                    general_area="Near Westgate Metro Station Exit B",
                    description="Encountered verbal catcalling and persistent following for two blocks. Reached lighted shop safely.",
                    severity="MEDIUM",
                    status="UNDER REVIEW"
                ),
                IncidentReport(
                    user_id=user.id,
                    incident_type="Unsafe Transportation",
                    incident_date=datetime.now() - timedelta(days=10),
                    general_area="Late night Bus Route 42",
                    description="Interior lights were switched off on late night bus and driver refused to stop at designated stop.",
                    severity="HIGH",
                    status="RESOLVED",
                    resolution_notes="Escalated to transit authority security division. Operator identified and assigned re-training.",
                    resolved_at=datetime.now() - timedelta(days=5),
                    resolved_by_admin_id=admin.id
                )
            ]
            db_session.add_all(sample_incidents)
            db_session.commit()

            # Add timeline entries
            for inc in sample_incidents:
                db_session.add(IncidentTimeline(
                    incident_id=inc.id,
                    actor_name="Elena Rostova",
                    actor_role="USER",
                    action="REPORT_SUBMITTED",
                    notes="Incident report recorded by user."
                ))
            db_session.commit()

        # 8. Seed Sample SOS Events for Analytics
        print("[+] Seeding sample SOS events...")
        if db_session.query(SOSEvent).count() == 0:
            resolved_sos = SOSEvent(
                user_id=user.id,
                status="RESOLVED",
                latitude=40.7128,
                longitude=-74.0060,
                address_note="5th Avenue Commercial Plaza",
                trigger_type="MANUAL",
                emergency_notes="Felt unsafe walking back from library",
                resolved_at=datetime.now() - timedelta(days=3),
                resolution_notes="User reached home safely. Verified via callback.",
                resolved_by="USER"
            )
            db_session.add(resolved_sos)
            db_session.commit()

            db_session.add(SOSAuditLog(
                sos_event_id=resolved_sos.id,
                action="ACTIVATED",
                actor_email=user.email,
                notes="Emergency SOS triggered."
            ))
            db_session.add(SOSAuditLog(
                sos_event_id=resolved_sos.id,
                action="RESOLVED",
                actor_email=user.email,
                notes="User marked alert as resolved."
            ))
            db_session.commit()

        # 9. Seed Initial Notifications
        print("[+] Seeding initial user notifications...")
        if db_session.query(Notification).filter_by(user_id=user.id).count() == 0:
            notifs = [
                Notification(
                    user_id=user.id,
                    title="Welcome to Women Safety Platform",
                    message="Your personal safety dashboard is ready. Begin by adding trusted emergency contacts.",
                    notification_type="System",
                    link_url="/contacts"
                ),
                Notification(
                    user_id=user.id,
                    title="Safety Checklist Reminder",
                    message="You have completed 3 of 6 precautions. Finish your checklist to boost your readiness score.",
                    notification_type="Checklist Reminder",
                    link_url="/checklist"
                )
            ]
            db_session.add_all(notifs)
            db_session.commit()

        # 10. Seed System Settings
        print("[+] Seeding system settings...")
        settings_data = [
            ("platform_name", "Women Safety & Emergency Assistance Platform", "Public display name"),
            ("sos_escalation_timeout", "15", "Active SOS escalation period in minutes"),
            ("official_disclaimer", app.config["DISCLAIMER_TEXT"], "Global emergency disclaimer"),
            ("readiness_disclaimer", app.config["READINESS_DISCLAIMER"], "Preparedness score disclaimer")
        ]
        for key, val, desc in settings_data:
            if not db_session.query(SystemSetting).filter_by(key=key).first():
                db_session.add(SystemSetting(key=key, value=val, description=desc))
        db_session.commit()

        # 11. Seed Audit Logs
        print("[+] Seeding security audit trail...")
        AuditLog_entries = [
            AuditLog(action="SYSTEM_INIT", category="SETTINGS", user_email="system", details="Database initialized and seeded with synthetic demo records."),
            AuditLog(action="USER_REGISTERED", category="AUTH", user_id=admin.id, user_email=admin.email, details="Initial administrator provisioned."),
            AuditLog(action="USER_REGISTERED", category="AUTH", user_id=user.id, user_email=user.email, details="Initial demonstration user provisioned.")
        ]
        db_session.add_all(AuditLog_entries)
        db_session.commit()

        print("[SUCCESS] Database successfully initialized and seeded with realistic demo data!")
        print(f"[*] Admin login: admin@womensafety.org / Admin@12345")
        print(f"[*] User login:  user@womensafety.org / User@12345")

if __name__ == "__main__":
    seed_database()
