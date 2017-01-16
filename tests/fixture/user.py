# pylint: disable=redefined-outer-name
import pytest

from models import User


@pytest.fixture
def user_token():
    return 'f70ed8110e46f06d8aa8e06c88a1634927c83fc3'


@pytest.yield_fixture
def create_user(session_db, user_token):
    user = None

    async def user_init(login='', password=''):
        nonlocal user
        conn = await session_db()
        user = await User.create_user(login, password, conn=conn)
        await User.add_token(user.id, token=user_token, conn=conn)

        return user

    yield user_init
