import datetime
import json
import time

import bcrypt
import hashlib
import sqlalchemy as sa
from aiopg.sa.result import RowProxy
from aiovalidator import abort
from functools import wraps

from models import User


def validate_password(password, user_password):
    password_hash = bcrypt.hashpw(password.encode(), user_password.encode())
    return user_password == password_hash.decode()


def generate_token(user_id):
    token = '%s-%s' % (time.time(), user_id)
    return hashlib.sha1(token.encode()).hexdigest()


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, RowProxy):
            return dict(obj)
        elif type(obj) == datetime.datetime:
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

        abort(status=401, text='Unauthorized')

    return wrapped
