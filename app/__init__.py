from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from sqlalchemy import MetaData
import sqlalchemy.orm as so


class Base(so.DeclarativeBase, so.MappedAsDataclass):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    })


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "agency.login"
login_manager.login_message_category = "warning"


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    from app.agency import bp as agency_bp
    app.register_blueprint(agency_bp, url_prefix="/agency")
    from app.client import bp as client_bp
    app.register_blueprint(client_bp, url_prefix="/client")
    from app.campaign import bp as campaign_bp
    app.register_blueprint(campaign_bp, url_prefix="/campaign")
    from app.lead import bp as lead_bp
    app.register_blueprint(lead_bp, url_prefix="/lead")
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix="/admin")
    from app.routes import bp
    app.register_blueprint(bp)
    return app


from app import models
