"""Models"""
import uuid

import pytz

from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType

from calichat.extensions import db, bcrypt


class UTCAwareDateTime(db.TypeDecorator):
    '''
    Custom column type.
    Results returned as aware datetimes, not naive ones.
    '''
    impl = db.DateTime

    def process_result_value(self, value, dialect):
        return value.replace(tzinfo=pytz.utc)


class User(db.Model, UserMixin):
    """Model for users"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True)
    _password = db.Column(db.String(128))

    @hybrid_property
    def password(self):
        """Password getter"""
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        """Password setter"""
        self._password = bcrypt.generate_password_hash(plaintext)

    def __repr__(self):
        return '<User %r>' % self.email

    def get_id(self):
        """
        Method for flask-login to extract the user
        """
        return str(self.email)

    def is_correct_password(self, plaintext):
        """
        Checks if the password is correct
        """
        return bcrypt.check_password_hash(self._password, plaintext)


class Room(db.Model):
    """Model for chat rooms"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(120), unique=True)


class Message(db.Model):
    """
    Model for messages in room

    NOTE: using a UUID4 as primary key to avoid risks of running out of integers.
    A UUID4 has a risk of collition of 1/(2^64 * 16)
    """
    uuid = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    message = db.Column(db.Text)
    timestamp = db.Column(UTCAwareDateTime, index=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id', ondelete='CASCADE'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship("User")
    message_type = db.Column(db.String(120))

    def to_json(self):
        """
        Serializes the object to a message
        """
        return {
            'id': self.uuid.hex,
            'content': self.message,
            'timestamp': self.timestamp.isoformat(),
            'sender': self.user.email,
            'message_type': self.message_type,
        }
