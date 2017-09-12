"""Utility functions"""
from datetime import datetime
from uuid import uuid4

import pytz


def create_message_structure(content, sender, message_type):
    """
    Creates a message dictionary
    """
    return {
        'content': content,
        'sender': sender,
        'message_type': message_type,
        'id': uuid4().hex,
        'timestamp': datetime.now(tz=pytz.UTC).isoformat()
    }


def create_user_message(content, sender):
    """
    Shortcut for create_message_structure user messages
    """
    return create_message_structure(content, sender, message_type='user_message')


def create_system_message(content):
    """
    Shortcut for create_message_structure user messages
    """
    return create_message_structure(content, sender='system', message_type='notification')
