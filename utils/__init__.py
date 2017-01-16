import datetime
from functools import wraps
import json

from aiohttp.hdrs import METH_ALL
from aiopg.sa.result import RowProxy
from aiovalidator import abort
import sqlalchemy as sa

from models.models import User


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
