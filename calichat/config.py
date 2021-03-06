"""App configuration object"""

import os
from calichat.envs import (
    get_bool,
    get_int,
    get_string,
)


class Config:
    """Class for base configuration"""

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    APP_VERSION = '0.0.1_alpha'
    DEBUG = get_bool('DEBUG', False)
    SECRET_KEY = get_string('SECRET_KEY', 'ls8t)o32h@bqp1s8e0&6+mepk#t4@^68yx43kjm_#tvdv=m&ke')
    PORT_NUMBER = get_int('PORT', 5000)
    SERVER_BASE_NAME = get_string('SERVER_BASE_NAME', 'calichat.local')
    SERVER_NAME = '{server_base_name}:{port_number}'.format(
        server_base_name=SERVER_BASE_NAME, port_number=PORT_NUMBER)
    SQLALCHEMY_DATABASE_URI = get_string(
        'DATABASE_URL', 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'calichat.db')))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CSRF_ENABLED = get_bool('CSRF_ENABLED', True)
    BCRYPT_LOG_ROUNDS = get_int('BCRYPT_LOG_ROUNDS', 12)
    SOCKET_NAMESPACE = '/chat'
    REDIS_URL = get_string('REDIS_URL', '')
