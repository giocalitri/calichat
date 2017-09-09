"""The actual app"""
from threading import Lock

from flask import (
    render_template,
    request,
    flash,
    redirect,
    url_for,
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


@app.route('/chat')
@login_required
def chat():
    return 'chat'


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if User.query.filter_by(email=form.email.data).first():
                flash("Email address already exists", 'error')
            else:
                newuser = User(email=form.email.data, password=form.password.data)
                db.session.add(newuser)
                db.session.commit()
                login_user(newuser)
                flash("User created!", 'success')
                return redirect(request.args.get('next') or url_for('index'))
        else:
            flash("Please enter valid data.", 'error')
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET','POST'])
def login():
    form = SignupForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                if user.is_correct_password(form.password.data):
                    login_user(user)
                    flash("User logged in", 'success')
                    return redirect(request.args.get('next') or url_for('index'))
                else:
                    flash("Wrong password", 'error')
            else:
                flash("User doesn't exist", 'error')
        else:
            flash("Please enter valid data.", 'error')
    return render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out", 'success')
    return redirect(url_for('index'))
