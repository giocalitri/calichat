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


def serialize_pagination(pagination_obj):
    """
    Returns a list of serialized objects for the elements in the iterable
    """
    return {
        'items': list(reversed([item.to_json() for item in pagination_obj.items])),
        'current_page': pagination_obj.page,
        'next_page': pagination_obj.next_num,
        'prev_page': pagination_obj.prev_num,
        'total_pages': pagination_obj.pages,
        'total_number_items': pagination_obj.total,
    }
