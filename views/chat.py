from aiohttp import web
from aiovalidator import IntegerField, StrField, abort
import sqlalchemy as sa

from models.models import Chat, Message, User, UserChat
from utils import auth, dumps
from views import BaseView


class List(BaseView):
    """
    Get chats
    """
    @auth
    async def get(self):
        join = sa.outerjoin(Chat, UserChat, sa.and_(
            UserChat.chat == Chat.id,
            UserChat.user == self.request['user'].id,
        ))
        query = sa.select([Chat, UserChat.user]).select_from(join)
        chat_list = await (await self.db.execute(query)).fetchall()
        return web.json_response(chat_list, dumps=dumps)


class Create(BaseView):
    """
    Create new chat
    """

    class Field:
        name = StrField(methods={'post'})

    @auth
    async def post(self):
        fields = self.request['fields']

        query = sa.insert(Chat).values(name=fields.name)
        chat = await (await self.db.execute(query)).fetchone()

        return web.json_response({
            'id': chat.id,
        })


class Login(BaseView):
    """
    Login to chat
    """

    class Field:
        id = IntegerField(methods={'post'})

    @auth
    async def post(self):
        # TODO: Check if user is already in chat
        fields = self.request['fields']

        query = sa.insert(UserChat).values(
            user=self.request['user'].id,
            chat=fields.id,
        )

        await self.db.execute(query)

        return web.json_response({})


class Logout(BaseView):
    """
    Logout from chat
    """

    class Field:
        id = IntegerField(methods={'post'})

    @auth
    async def post(self):
        # TODO: Check if user is in chat
        fields = self.request['fields']

        query = sa.delete(UserChat).where(
            sa.and_(
                UserChat.user == self.request['user'].id,
                UserChat.chat == fields.id,
            )
        )
        await self.db.execute(query)

        return web.json_response({})


class Users(BaseView):
    """
    Get chat users
    """

    class Field:
        id = IntegerField(methods={'get'})

    async def get(self):
        # TODO: Implement
        raise abort(status=400, text='Not Implemented')


class History(BaseView):
    """
    Get chat history
    """

    class Field:
        id = IntegerField(methods={'get'})
        limit = IntegerField(methods={'get'}, default=10)
        last_id = IntegerField(methods={'get'}, required=False)

    @auth
    async def get(self):
        fields = self.request['fields']

        where = [
            Message.chat == fields.id,
        ]
        if fields.last_id:
            where.append(Message.id < fields.last_id)

        join = sa.join(Message, User, User.id == Message.user)
        query = sa.select([
            Message.id,
            Message.message,
            Message.datetime,
            User.login,
        ]).select_from(join)
        query = query.where(sa.and_(*where)).order_by(
            sa.desc(Message.id)).limit(fields.limit)

        history = await (await self.db.execute(query)).fetchall()
        return web.json_response(list(reversed(history)), dumps=dumps)


class Post(BaseView):
    """
    Post to chat
    """

    class Field:
        id = IntegerField(methods={'post'})
        message = StrField(methods={'post'})

    @auth
    async def post(self):
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

        message = await (await self.db.execute(query)).fetchone()
        message = dict(message)
        message['login'] = self.request['user'].login

        # TODO: Send `message` to websocket

        return web.json_response({})
