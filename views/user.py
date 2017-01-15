from aiohttp import web
from aiovalidator import StrField, abort
import bcrypt
import sqlalchemy as sa

from models.models import User
from utils import generate_token, validate_password

from . import BaseView


class Auth(BaseView):
    """
    User auth and register
    """

    class Field:
        login = StrField(methods={'post'})
        password = StrField(methods={'post'})

    async def post(self):
        fields = self.request['fields']
        conn = self.request['conn']

        if not all([fields.login, fields.password]):
            raise abort(status=400, text='Bad Request')

        query = sa.select([
            User]).select_from(User).where(User.login == fields.login)

        user = await (await conn.execute(query)).fetchone()

        if user:
            if not validate_password(fields.password, user.password):
                raise abort(status=418, text='Wrong password')
        else:
            password_hash = bcrypt.hashpw(
                fields.password.encode(),
                bcrypt.gensalt(),
            )
            query = sa.insert(User).values(
                login=fields.login,
                password=password_hash.decode(),
            )
            user = await (await conn.execute(query)).fetchone()

        token = generate_token(user.id)
        query = sa.update(User).where(User.id == user.id).values(
            token=token,
        )
        await conn.execute(query)

        return web.json_response({
            'success': True,
            'token': token,
        })
