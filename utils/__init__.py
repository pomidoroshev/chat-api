import datetime
from functools import wraps
import hashlib
import json
import time

import bcrypt
import sqlalchemy as sa
from aiohttp.hdrs import METH_ALL
from aiopg.sa.result import RowProxy
from aiovalidator import abort

from models.models import User


def validate_password(password, user_password):
    password_hash = bcrypt.hashpw(password.encode(), user_password.encode())
    return user_password == password_hash.decode()


def generate_token(user_id):
    token = '%s-%s' % (time.time(), user_id)
    return hashlib.sha1(token.encode()).hexdigest()


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):  # pylint: disable=method-hidden
        if isinstance(obj, RowProxy):
            return dict(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')

        return json.JSONEncoder.default(self, obj)


def dumps(data):
    return json.dumps(data, ensure_ascii=False, cls=JSONEncoder)


def auth(fn):
    @wraps(fn)
    async def wrapped(cls):
        headers = cls.request.headers
        if headers.get('X-Auth-Token'):
            token = headers['X-Auth-Token']
            conn = cls.request['conn']
            query = sa.select([User]).select_from(User).where(
                User.token == token)
            res = await conn.execute(query)
            user = await res.fetchone()

            if user:
                cls.request['user'] = user
                return await fn(cls)
        raise abort(status=401, text='Unauthorized')

    return wrapped


def set_default_headers(headers):
    headers['Access-Control-Allow-Origin'] = '*'
    headers['Access-Control-Allow-Credentials'] = 'true'
    headers['Access-Control-Allow-Headers'] = (
        'Cache-control, '
        'Accept, '
        'X-auth-token, '
        'Content-type, '
        'WWW-Authenticate')
    headers['Access-Control-Allow-Methods'] = ','.join(METH_ALL)
