from aiohttp import web, WSMsgType
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

        query = sa.insert(UserChat).values(
            user=self.request['user'].id,
            chat=chat.id,
        )

        await self.db.execute(query)

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
        msg = dumps(message)
        if fields.id in self.request.app['websockets']:
            for ws in self.request.app['websockets'][fields.id]:
                ws.send_str(msg)

        return web.json_response({})


class Websocket(web.View):
    async def get(self):
        chat_id = int(self.request.match_info['id'])
        if chat_id not in self.request.app['websockets']:
            self.request.app['websockets'][chat_id] = set()

        try:
            ws_response = web.WebSocketResponse()
            await ws_response.prepare(self.request)

            async for msg in ws_response:
                if msg.type == WSMsgType.TEXT:
                    if msg.data == 'close':
                        await ws_response.close()
                    elif msg.data.startswith('open'):
                        self.request.app['websockets'][chat_id].add(
                            ws_response)
                    else:
                        ws_response.send_str(msg.data)

                elif msg.type == WSMsgType.ERROR:
                    # TODO: Replace with logging
                    print('Websocket exception %s', ws_response.exception())

            if ws_response in self.request.app['websockets'][chat_id]:
                self.request.app['websockets'][chat_id].discard(ws_response)
        finally:
            pass

        return ws_response
