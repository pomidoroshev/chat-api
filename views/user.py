import bcrypt
import sqlalchemy as sa
from aiohttp import web
from aiovalidator import StrField, abort

from models import User
from utils import validate_password, generate_token


class Auth(web.View):
    """
    User auth and register
    """

    class Field:
        login = StrField(methods={'post'})
        password = StrField(methods={'post'})

    async def post(self):
        fields = self.request['fields']
        conn = self.request['conn']

        query = sa.select([
            User]).select_from(User).where(User.login == fields.login)

        res = await conn.execute(query)
        user = await res.fetchone()

        if user:
            if not validate_password(fields.password, user.password):
                abort(status=418, text='Wrong password')
        else:
            password_hash = bcrypt.hashpw(
                fields.password.encode(),
                bcrypt.gensalt(),
            )
            query = sa.insert(User).values(
                login=fields.login,
                password=password_hash.decode(),
            )
            res = await conn.execute(query)
            user = await res.fetchone()

        token = generate_token(user.id)
        query = sa.update(User).where(User.id == user.id).values(
            token=token,
        )
        await conn.execute(query)

        return web.json_response({
            'success': True,
            'token': token,
        })
