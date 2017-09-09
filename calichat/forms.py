"""forms for the app"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Email, DataRequired


class SignupForm(FlaskForm):
    """Signup form"""
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField("Sign In")


class RoomForm(FlaskForm):
    """Form for rooms"""
    title = StringField('title', validators=[DataRequired()])
    submit = SubmitField("Create new room")
