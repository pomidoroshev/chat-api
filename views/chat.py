from aiohttp import web
from aiovalidator import IntegerField, StrField, abort
import sqlalchemy as sa

from models.models import Chat, Message, User, UserChat
from utils import auth, dumps


class List(web.View):
    """
    Get chats
    """
    @auth
    async def get(self):
        conn = self.request['conn']
        join = sa.outerjoin(Chat, UserChat, sa.and_(
            UserChat.chat == Chat.id,
            UserChat.user == self.request['user'].id,
        ))
        query = sa.select([Chat, UserChat.user]).select_from(join)
        res = await conn.execute(query)
        chat_list = await res.fetchall()
        return web.json_response(chat_list, dumps=dumps)


class Create(web.View):
    """
    Create new chat
    """

    class Field:
        name = StrField(methods={'post'})

    @auth
    async def post(self):
        conn = self.request['conn']
        fields = self.request['fields']

        query = sa.insert(Chat).values(name=fields.name)
        chat = await (await conn.execute(query)).fetchone()

        return web.json_response({
            'id': chat.id,
        })


class Login(web.View):
    """
    Login to chat
    """

    class Field:
        id = IntegerField(methods={'post'})

    @auth
    async def post(self):
        conn = self.request['conn']
        fields = self.request['fields']

        query = sa.insert(UserChat).values(
            user=self.request['user'].id,
            chat=fields.id,
        )

        await conn.execute(query)

        return web.json_response({})


class Logout(web.View):
    """
    Logout from chat
    """

    class Field:
        id = IntegerField(methods={'post'})

    @auth
    async def post(self):
        conn = self.request['conn']
        fields = self.request['fields']

        query = sa.delete(UserChat).where(
            sa.and_(
                UserChat.user == self.request['user'].id,
                UserChat.chat == fields.id,
            )
        )
        await conn.execute(query)

        return web.json_response({})


class Users(web.View):
    """
    Get chat users
    """

    class Field:
        id = IntegerField(methods={'get'})

    async def get(self):
        # TODO: Implement
        raise abort(status=400, text='Not Implemented')


class History(web.View):
    """
    Get chat history
    """

    class Field:
        id = IntegerField(methods={'get'})
        offset = IntegerField(methods={'get'}, required=False)

    @auth
    async def get(self):
        conn = self.request['conn']
        fields = self.request['fields']

        join = sa.join(Message, User, User.id == Message.user)
        query = sa.select([
            Message.id,
            Message.message,
            Message.datetime,
            User.login,
        ]).select_from(join)
        query = query.where(
            Message.chat == fields.id).order_by(sa.desc(Message.id))

        res = await conn.execute(query)
        history = await res.fetchall()
        return web.json_response(history, dumps=dumps)


class Post(web.View):
    """
    Post to chat
    """

    class Field:
        id = IntegerField(methods={'post'})
        message = StrField(methods={'post'})

    @auth
    async def post(self):
        conn = self.request['conn']
        fields = self.request['fields']

        query = sa.insert(Message).values(
            user=self.request['user'].id,
            chat=fields.id,
            message=fields.message,
        ).returning(
            Message.id,
            Message.message,
            Message.datetime,
        )

        res = await conn.execute(query)
        message = await res.fetchone()
        message = dict(message)
        message['login'] = self.request['user'].login

        # TODO: Send `message` to websocket

        return web.json_response({})
