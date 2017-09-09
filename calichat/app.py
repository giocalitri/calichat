"""
defines the base app and the configuration
"""

from flask import Flask

from calichat.config import Config
from calichat.extensions import (
    db,
    login_manager,
    bcrypt,
)
from calichat.models import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # configure and initialize the database
    db.init_app(app)
    with app.test_request_context():
        # hack to automatically create all the tables
        db.create_all()

    # configure the login manager
    login_manager.init_app(app)

    login_manager.login_view = 'login'
    login_manager.needs_refresh_message = (u"To protect your account, please re-authenticate to access this page.")
    login_manager.needs_refresh_message_category = "info"

    @login_manager.user_loader
    def load_user(email):
        return User.query.filter_by(email=email).first()

    # configure bcrypt
    bcrypt.init_app(app)

    return app