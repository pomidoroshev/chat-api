import json

import sqlalchemy as sa

from models.models import Chat


async def test_options(cli):
    resp = await cli.options('/chat/list')
    assert resp.headers['Allow'] == 'GET,OPTIONS'


async def test_unauth(cli):
    resp = await cli.get('/chat/list')
    assert resp.status == 401


async def test_chat_create(cli, create_user, user_token, session_db):
    await session_db()
    await create_user()

    resp = await cli.post('/chat/create', headers={
        'X-Auth-Token': user_token,
    }, data=json.dumps({
        'name': 'Chat'
    }))
    assert resp.status == 200


async def test_chat_list(cli, create_user, user_token, session_db):
    db = await session_db()
    await create_user()

    chats = [
        {
            'name': 'Chat1',
            'user': None,
        },
        {
            'name': 'Chat2',
            'user': None,
        },
    ]

    for chat in chats:
        query = sa.insert(Chat).values(name=chat['name'])
        new_chat = await (await db.execute(query)).fetchone()
        chat['id'] = new_chat['id']

    resp = await cli.get('/chat/list', headers={
        'X-Auth-Token': user_token,
    })
    assert resp.status == 200
    assert await resp.json() == chats


async def test_chat_login_logout(cli, user_token, session_db, create_user):
    db = await session_db()
    await create_user()

    query = sa.insert(Chat).values(name='Chat')
    chat = await (await db.execute(query)).fetchone()

    resp = await cli.post('/chat/%s/login' % chat.id, headers={
        'X-Auth-Token': user_token,
    })

    assert resp.status == 200

    resp = await cli.post('/chat/%s/logout' % chat.id, headers={
        'X-Auth-Token': user_token,
    })

    assert resp.status == 200


async def test_chat_post_history(cli, session_db, create_user, user_token):
    await session_db()
    await create_user()

    resp = await cli.post('/chat/create', headers={
        'X-Auth-Token': user_token,
    }, data=json.dumps({
        'name': 'Chat'
    }))
    assert resp.status == 200
    chat_id = (await resp.json())['id']

    resp = await cli.post('/chat/%s/post' % chat_id, headers={
        'X-Auth-Token': user_token,
    }, data=json.dumps({
        'message': 'Hello!'
    }))
    assert resp.status == 200

    resp = await cli.get('/chat/%s/history' % chat_id, headers={
        'X-Auth-Token': user_token,
    })
    assert resp.status == 200
    assert len(await resp.json()) == 1
