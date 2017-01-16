from datetime import datetime  # pylint: disable=unused-import

import bcrypt
import sqlalchemy as sa

from utils.user import generate_token
from .base import Base

__all__ = [
    'Chat',
    'Message',
    'User',
    'UserChat',
]


class Chat(Base):
    __tablename__ = 'chat'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(255))


class Message(Base):
    __tablename__ = 'message'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    datetime = sa.Column(sa.DateTime, default=datetime.now)
    chat = sa.Column(
        sa.ForeignKey('chat.id', deferrable=True, initially='DEFERRED'),
        nullable=False,
        index=True,
    )
    user = sa.Column(
        sa.ForeignKey('user.id', deferrable=True, initially='DEFERRED'),
        nullable=False,
    )
    message = sa.Column(sa.Text)


class User(Base):
    __tablename__ = 'user'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    login = sa.Column(sa.String(255), index=True)
    password = sa.Column(sa.String(255))
    token = sa.Column(sa.String(40), index=True)

    @staticmethod
    async def add_token(user_id, *, conn, **kwargs):
        if 'token' in kwargs:
            user_token = kwargs['token']
        else:
            user_token = generate_token(user_id)
        query = sa.update(User).where(User.id == user_id).values(
            token=user_token,
        )
        await conn.execute(query)
        return user_token

    @staticmethod
    async def create_user(login, password, *, conn):
        password_hash = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt(),
        )
        query = sa.insert(User).values(
            login=login,
            password=password_hash.decode(),
        )
        return await (await conn.execute(query)).fetchone()


class UserChat(Base):
    __tablename__ = 'user_chat'
    __table_args__ = (
        sa.UniqueConstraint('user', 'chat'),
    )

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user = sa.Column(
        sa.ForeignKey('user.id', deferrable=True, initially='DEFERRED'),
        index=True,
        nullable=False,
    )
    chat = sa.Column(
        sa.ForeignKey('chat.id', deferrable=True, initially='DEFERRED'),
        index=True,
        nullable=False,
    )
