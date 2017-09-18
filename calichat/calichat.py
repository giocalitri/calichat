"""
Module Containing the definition of the flask app
"""
# Monkey patching of the standard library needs to be done before any other import
from gevent import monkey
monkey.patch_all()

from functools import wraps
from threading import Lock

from flask import (
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_socketio import (
    disconnect,
    emit,
    join_room,
    leave_room,
    Namespace,
    SocketIO,
)
from sqlalchemy import (
    desc,
    func,
)
from sqlalchemy.exc import StatementError

from calichat.app import create_app
from calichat.config import Config
from calichat.extensions import db
from calichat.forms import SignupForm, RoomForm
from calichat.models import (
    Message,
    Room,
    User,
)
from calichat.utils import (
    create_user_message,
    create_system_message,
    serialize_pagination,
)

app = create_app()

socketio = SocketIO(app, async_mode=None,  message_queue=Config.REDIS_URL)
thread = None
thread_lock = Lock()


@app.route('/')
def index():
    """Index page."""
    if current_user.is_authenticated:
        return redirect(url_for('room_list'))
    return render_template('index.html')


@app.route('/room/', methods=['GET', 'POST'])
@login_required
def room_list():
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
                return redirect(url_for('room_list'))
    chat_rooms = Room.query.order_by(func.lower(Room.title)).all()
    return render_template('room_list.html', form=form, chat_rooms=chat_rooms)


@app.route('/room/<int:room_id>/')
@login_required
def room_detail(room_id):
    """
    The room where the chat happens
    """
    room = Room.query.filter_by(id=room_id).first_or_404()
    old_messages = serialize_pagination(
        Message.query.filter_by(room_id=room_id).order_by(desc(Message.timestamp)).paginate()
    )
    return render_template('room_with_chat.html', chat_room=room, old_messages=old_messages)


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
                return redirect(request.args.get('next') or url_for('room_list'))
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
                    return redirect(request.args.get('next') or url_for('room_list'))
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


@app.route("/api/v0/room/<int:room_id>/messages/")
@login_required
def get_old_messages(room_id):
    """
    REST view to get the old messages.
    """
    Room.query.filter_by(id=room_id).first_or_404()
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    old_messages = serialize_pagination(
        Message.query.filter_by(
            room_id=room_id).order_by(desc(Message.timestamp)).paginate(page=page, error_out=False)
    )
    return jsonify(old_messages)


def login_required_socket(func):
    """Custom decorator to be used on websockets definitions"""
    @wraps(func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return func(*args, **kwargs)
    return wrapped


class ChatNamespace(Namespace):
    """Socketio definitions"""

    @login_required_socket
    def on_connect(self):
        """Handler for connection"""
        response_json, _ = create_system_message('You are connected, {}'.format(current_user.email))
        emit(
            'chat_response',
            response_json
        )

    @login_required_socket
    def on_disconnect(self):
        """Handler for disconnection"""
        response_json, _ = create_system_message('Disconnected')
        emit('chat_response', response_json)

    @login_required_socket
    def on_room_event(self, message_json):
        """Handler to send a message in a room"""
        response_json, timestamp = create_user_message(message_json['content'], current_user.email)
        emit(
            'chat_response',
            response_json,
            room=message_json['room_id']
        )

        message_in_db = Message(
            uuid=response_json['id'],
            message=response_json['content'],
            timestamp=timestamp,
            room_id=message_json['room_id'],
            user_id=current_user.id,
            message_type=response_json['message_type'],
        )
        db.session.add(message_in_db)
        db.session.commit()

    @login_required_socket
    def on_join_room(self, message_json):
        """Handler to join a room"""
        # TODO: verify that the room id exists
        join_room(message_json['room_id'])
        response_json, _ = create_system_message('{} joined the room'.format(current_user.email))
        emit(
            'chat_response',
            response_json,
            room=message_json['room_id']
        )

    @login_required_socket
    def on_leave_room(self, message_json):
        """Handler to leave a room"""
        leave_room(message_json['room_id'])
        response_json, _ = create_system_message('{} left the room'.format(current_user.email))
        emit(
            'chat_response',
            response_json,
            room=message_json['room_id']
        )

    @login_required_socket
    def on_delete_message(self, message_json):
        """
        Handler to delete a message.
        This checks that the user that tries to delete it, is the massage writer
        """
        message_id = message_json['message_id']
        try:
            message_in_db = Message.query.get(message_id)
        except StatementError:
            emit(
                'error_response',
                {'content': 'The server has no knowledge of this message'}
            )
            return
        try:
            if message_in_db.user != current_user:
                emit(
                    'error_response',
                    {'content': 'You are not allowed to delete this message'}
                )
                return
        except AttributeError:
            pass
        # perfom the actual deletion in the database
        db.session.delete(message_in_db)
        db.session.commit()

        emit(
            'delete_message_response',
            {'message_id': message_id},
            room=message_json['room_id']
        )


socketio.on_namespace(ChatNamespace(app.config['SOCKET_NAMESPACE']))
