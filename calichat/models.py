"""Models"""
from flask_login import UserMixin

from calichat.extensions import db


class User(db.Model, UserMixin):
    email = db.Column(db.String(80), primary_key=True, unique=True)
    password = db.Column(db.String(80))

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

    def get_id(self):
        """needs to be an unique string"""
        return str(self.email)
