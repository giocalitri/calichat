"""extensions initialization for the app"""

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# the database instance
db = SQLAlchemy()

# the login manager
login_manager = LoginManager()
