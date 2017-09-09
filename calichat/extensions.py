"""extensions initialization for the app"""

from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# the database instance
db = SQLAlchemy()

# the login manager
login_manager = LoginManager()

# bcrypt
bcrypt = Bcrypt()
