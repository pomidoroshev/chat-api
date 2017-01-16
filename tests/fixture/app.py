# pylint: disable=redefined-outer-name
import json

import pytest
from aiopg.sa import create_engine

from main import create_app
from conf import settings as app_settings
from defaultenv import ENV

app_settings.DATABASE['dbname'] = ENV.DB_NAME_TEST


class MonkeyPatchWrapper(object):

    def __init__(self, monkeypatch, wrapped_object):
        super(MonkeyPatchWrapper, self).__setattr__(
            'monkeypatch',
            monkeypatch,
        )
        super(MonkeyPatchWrapper, self).__setattr__(
            'wrapped_object',
            wrapped_object,
        )

    def __getattr__(self, attr):
        return getattr(self.wrapped_object, attr)

    def __setattr__(self, attr, value):
        self.monkeypatch.setattr(
            self.wrapped_object,
            attr,
            value,
            raising=False,
        )

    def __delattr__(self, attr):
        self.monkeypatch.delattr(self.wrapped_object, attr)


@pytest.fixture
def settings(monkeypatch):
    return MonkeyPatchWrapper(monkeypatch, app_settings)


@pytest.fixture
def json_dumps():
    return json.dumps


@pytest.fixture
def json_loads():
    return json.loads


@pytest.fixture
def cli(loop, test_client, monkeypatch):
    monkeypatch.setattr('aiohttp_autoreload.start', lambda: None)
    return loop.run_until_complete(test_client(create_app))


@pytest.yield_fixture
def session_db(loop, settings):
    conn = None

    async def db_connect():
        nonlocal conn
        if conn:
            return conn
        engine = await create_engine(
            **settings.DATABASE,
            loop=loop
        )
        conn = await engine.acquire()
        await conn.execute("""
            delete from message;
            delete from chat;
            delete from user_chat;
            delete from "user";
        """)
        return conn

    yield db_connect
    if conn:
        yield from conn.close()


@pytest.yield_fixture
def file_open():
    file = None

    def opener(filename, mode):
        nonlocal file
        assert file is None
        file = open(filename, mode)
        return file

    yield opener

    if file is not None:
        file.close()
