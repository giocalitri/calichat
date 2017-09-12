"""Utility functions"""
from datetime import datetime
from uuid import uuid4

import pytz


def create_message_structure(content, sender, message_type):
    """
    Creates a message dictionary
    """
    raw_timestamp = datetime.now(tz=pytz.UTC)
    message = {
        'id': uuid4().hex,
        'content': content,
        'timestamp': raw_timestamp.isoformat(),
        'sender': sender,
        'message_type': message_type,
    }
    return message, raw_timestamp


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
