import pytest
from app import create_app
from app.database import create_all_tables, drop_all_tables, db_session
from app.models.user import Role, User
from app.models.checklist import ChecklistItem
from app.models.resource import EmergencyResource
from app.models.tip import SafetyTip
from app.security.hashing import hash_password

@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    with app.app_context():
        yield app

@pytest.fixture(autouse=True)
def init_database(app):
    with app.app_context():
        create_all_tables()

        # Seed roles
        user_role = Role(name="USER", description="Standard User")
        admin_role = Role(name="ADMIN", description="Admin User")
        db_session.add_all([user_role, admin_role])
        db_session.commit()

        # Seed baseline checklist items
        checklist_items = [
            ChecklistItem(title="Add Emergency Contacts", description="Add at least 2 contacts", category="Contacts", sort_order=1),
            ChecklistItem(title="Save Emergency Hotline", description="Save police and medical numbers", category="Contacts", sort_order=2),
            ChecklistItem(title="Review Safe Havens", description="Review local hospitals and centers", category="Preparedness", sort_order=3)
        ]
        db_session.add_all(checklist_items)

        # Seed baseline resource
        resource = EmergencyResource(
            name="City Central Police Station",
            category="Police Station",
            city="Metropolis",
            general_area="Main Square",
            demo_phone="1091",
            description="Dedicated women safety unit.",
            latitude=40.7128,
            longitude=-74.0060,
            is_active=True
        )
        db_session.add(resource)

        # Seed baseline tip
        tip = SafetyTip(
            title="Night Transit Safety",
            category="Night Travel",
            summary="Essential habits for safe night transit.",
            content="Stay in well-lit areas and avoid distraction with phones.",
            read_time_minutes=3,
            is_published=True
        )
        db_session.add(tip)

        db_session.commit()

        yield

        db_session.rollback()
        drop_all_tables()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(app):
    with app.app_context():
        user_role = db_session.query(Role).filter_by(name="USER").first()
        user = User(
            email="testuser@womensafety.org",
            password_hash=hash_password("UserPass@123"),
            full_name="Test User",
            phone="+1 555-0101",
            city="Metropolis",
            role_id=user_role.id,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

@pytest.fixture
def test_admin(app):
    with app.app_context():
        admin_role = db_session.query(Role).filter_by(name="ADMIN").first()
        admin = User(
            email="testadmin@womensafety.org",
            password_hash=hash_password("AdminPass@123"),
            full_name="Test Admin",
            phone="+1 555-0199",
            city="Metropolis",
            role_id=admin_role.id,
            is_active=True
        )
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)
        return admin

@pytest.fixture
def auth_user_client(client, test_user):
    with client.session_transaction() as sess:
        sess["user_id"] = test_user.id
        sess["user_email"] = test_user.email
        sess["user_name"] = test_user.full_name
        sess["user_role"] = "USER"
    return client

@pytest.fixture
def auth_admin_client(client, test_admin):
    with client.session_transaction() as sess:
        sess["user_id"] = test_admin.id
        sess["user_email"] = test_admin.email
        sess["user_name"] = test_admin.full_name
        sess["user_role"] = "ADMIN"
    return client
