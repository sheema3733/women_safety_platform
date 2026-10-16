from flask import Flask
from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.user import user_bp
from app.routes.contacts import contacts_bp
from app.routes.sos import sos_bp
from app.routes.incidents import incidents_bp
from app.routes.resources import resources_bp
from app.routes.tips import tips_bp
from app.routes.checklist import checklist_bp
from app.routes.notifications import notifications_bp
from app.routes.admin import admin_bp
from app.routes.analytics import analytics_bp
from app.routes.reports import reports_bp
from app.routes.api import api_bp

def register_blueprints(app: Flask):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(sos_bp)
    app.register_blueprint(incidents_bp)
    app.register_blueprint(resources_bp)
    app.register_blueprint(tips_bp)
    app.register_blueprint(checklist_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(api_bp)
