import pytest

from models import User


@pytest.yield_fixture
def create_user(session_db):
    user = None

    async def user_init(login, password):
        nonlocal user
        token = 'f70ed8110e46f06d8aa8e06c88a1634927c83fc3'
        conn = await session_db()
        user = await User.create_user(login, password, conn=conn)
        await User.add_token(user.id, token=token, conn=conn)

        return user

    yield user_init
