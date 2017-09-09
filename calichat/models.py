"""Models"""
import uuid

from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID

from calichat.extensions import db, bcrypt


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    credits to:
    http://docs.sqlalchemy.org/en/rel_0_9/core/custom_types.html?highlight=guid#backend-agnostic-guid-type
    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)


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
        return '<User %r>' % self.username

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
    name = db.Column(db.String(120))


class Message(db.Model):
    """
    Model for messages in room

    NOTE: using a UUID4 as primary key to avoid risks of running out of integers.
    A UUID4 has a risk of collition of 1/(2^64 * 16)
    """
    uuid = db.Column(GUID, primary_key=True)
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
