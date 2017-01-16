from functools import wraps

from aiovalidator import abort
import sqlalchemy as sa

from models.models import User


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
