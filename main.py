"""
Main chat module
"""

import asyncio

from aiohttp import web, WSCloseCode
import aiohttp_autoreload
from aiopg.sa import create_engine
from aiovalidator import middleware_exception, validator_factory

from conf import settings
from middlewares import crossdomain, db
from urls import urls


async def start_background_tasks(app: web.Application):
    """
    Establish database connection
    """
    app['db'] = await create_engine(**settings.DATABASE, loop=app.loop)
    app['websockets'] = dict()


async def stop_background_tasks(app: web.Application):
    """
    Close database connection
    """
    for channel in app['websockets']:
        for websocket in app['websockets'][channel]:
            await websocket.close(
                code=WSCloseCode.GOING_AWAY,
                message='Server shutdown',
            )

    app['db'].close()
    await app['db'].wait_closed()


def create_app(loop=None):
    """
    Create app
    """
    if loop is None:
        loop = asyncio.get_event_loop()

    if settings.DEBUG:
        aiohttp_autoreload.start()

    app = web.Application(
        middlewares=[
            crossdomain,
            validator_factory(),
            middleware_exception,
            db,
        ],
        debug=settings.DEBUG,
        loop=loop,
    )

    for url in urls:
        app.router.add_route(*url)

    app.on_startup.append(start_background_tasks)
    app.on_shutdown.append(stop_background_tasks)

    return app


if __name__ == '__main__':
    web.run_app(create_app(), port=settings.PORT)
