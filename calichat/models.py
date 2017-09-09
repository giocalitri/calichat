"""Models"""
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property

from calichat.extensions import db, bcrypt


class User(db.Model, UserMixin):
    email = db.Column(db.String(120), primary_key=True, unique=True)
    _password = db.Column(db.String(128))

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext)

    def __repr__(self):
        return '<User %r>' % self.username

    def get_id(self):
        """needs to be an unique string"""
        return str(self.email)

    def is_correct_password(self, plaintext):
        """
        Checks if the password is correct
        """
        return bcrypt.check_password_hash(self._password, plaintext)
