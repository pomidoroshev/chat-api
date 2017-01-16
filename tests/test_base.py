import json


async def test_main(cli):
    resp = await cli.get('/')
    assert resp.status == 404
    assert await resp.json() == {"message": "Not Found"}


async def test_user_auth(cli, create_user):
    await create_user('some_login', 'some_password')
    resp = await cli.post('/auth', data=json.dumps({
        'login': 'some_login',
        'password': 'some_password'
    }))
    assert resp.status == 200
    token = await resp.json()
    assert 'token' in token


async def test_user_auth_wrong_password(cli, create_user):
    await create_user('some_login', 'some_password')
    resp = await cli.post('/auth', data=json.dumps({
        'login': 'some_login',
        'password': 'some_other_password'
    }))
    assert resp.status == 418


async def test_user_create(cli, session_db):
    await session_db()
    resp = await cli.post('/auth', data=json.dumps({
        'login': 'some_login',
        'password': 'some_password'
    }))
    assert resp.status == 200
    token = await resp.json()
    assert 'token' in token


async def test_user_auth_bad_request(cli):
    resp = await cli.post('/auth', data=json.dumps({
        'login': 'some_login',
    }))
    assert resp.status == 406

    resp = await cli.post('/auth', data=json.dumps({
        'login': 'some_login',
        'password': '',
    }))
    assert resp.status == 400

# async def test_chat_list(cli):
#     pass


# async def test_chat_create(cli):
#     pass


# async def test_chat_login(cli):
#     pass


# async def test_chat_logout(cli):
#     pass


# async def test_chat_users(cli):
#     pass


# async def test_chat_history(cli):
#     pass


# async def test_chat_post(cli):
#     pass
