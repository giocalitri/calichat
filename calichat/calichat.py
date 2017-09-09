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
    current_user,
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
from sqlalchemy.sql import collate

from calichat.app import create_app
from calichat.extensions import db
from calichat.forms import SignupForm, RoomForm
from calichat.models import User, Room

app = create_app()

socketio = SocketIO(app, async_mode=None)
thread = None
thread_lock = Lock()


@app.route('/')
def index():
    """Index page."""
    if current_user.is_authenticated:
        return redirect(url_for('rooms'))
    return render_template('index.html')


@app.route('/room', methods=['GET', 'POST'])
@login_required
def rooms():
    """Lists rooms and allows to create new ones"""
    form = RoomForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if Room.query.filter_by(title=form.title.data).first():
                flash("Room with same name already exists", 'error')
            else:
                new_room = Room(title=form.title.data)
                db.session.add(new_room)
                db.session.commit()
                return redirect(url_for('rooms'))
    chat_rooms = Room.query.order_by(collate(Room.title, 'NOCASE')).all()
    return render_template('rooms.html', form=form, chat_rooms=chat_rooms)


@app.route('/room/<int:room_id>/')
@login_required
def room(room_id):
    """
    The room where the chat happens
    """
    room = Room.query.filter_by(id=room_id).first_or_404()
    return render_template('room_with_chat.html', chat_room=room)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Takes care of creating new users"""
    form = SignupForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if User.query.filter_by(email=form.email.data).first():
                flash("Email address already exists", 'error')
            else:
                new_user = User(email=form.email.data, password=form.password.data)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                flash("User created!", 'success')
                return redirect(request.args.get('next') or url_for('rooms'))
        else:
            flash("Please enter valid data.", 'error')
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET','POST'])
def login():
    """Takes car of logging in the user"""
    form = SignupForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                if user.is_correct_password(form.password.data):
                    login_user(user)
                    flash("User logged in", 'success')
                    return redirect(request.args.get('next') or url_for('rooms'))
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
    """Takes care of logging out the user"""
    logout_user()
    flash("Logged out", 'success')
    return redirect(url_for('index'))
