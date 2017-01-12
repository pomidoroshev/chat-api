from datetime import datetime

import sqlalchemy as sa

from models.base import Base

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
