from aiohttp import web
from aiovalidator import StrField, abort

import sqlalchemy as sa

from models.models import User
from utils.user import validate_password

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
            user = await User.create_user(
                fields.login,
                fields.password,
                conn=conn,
            )

        token = await User.add_token(user.id, conn=conn)

        return web.json_response({
            'token': token,
        })
