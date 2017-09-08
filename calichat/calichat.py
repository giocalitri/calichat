"""The actual app"""
from threading import Lock

from flask import (
    render_template,
    request,
)
from flask_login import (
    login_user,
    login_required,
    logout_user,
)
from flask_socketio import (
    SocketIO,
    Namespace,
    emit,
    join_room,
    leave_room,
    close_room,
    rooms,
    disconnect,
)

from calichat.app import create_app
from calichat.extensions import db
from calichat.forms import SignupForm
from calichat.models import User

app = create_app()

socketio = SocketIO(app, async_mode=None)
thread = None
thread_lock = Lock()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if request.method == 'GET':
        return render_template('signup.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            if User.query.filter_by(email=form.email.data).first():
                return "Email address already exists"
            else:
                newuser = User(form.email.data, form.password.data)
                db.session.add(newuser)
                db.session.commit()
                login_user(newuser)
                return "User created!!!"
        else:
            return "Form didn't validate"


@app.route('/protected')
@login_required
def protected():
    return "protected area"


@app.route('/login', methods=['GET','POST'])
def login():
    form = SignupForm()
    if request.method == 'GET':
        return render_template('login.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                if user.password == form.password.data:
                    login_user(user)
                    return "User logged in"
                else:
                    return "Wrong password"
            else:
                return "user doesn't exist"
        else:
            return "form not validated"


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return "Logged out"
