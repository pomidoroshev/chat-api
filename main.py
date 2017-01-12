import asyncio

import aiohttp_autoreload
from aiohttp import web
from aiopg.sa import create_engine
from aiovalidator import (
    validator_factory,
    middleware_exception,
)

from conf import settings
from middlewares import db
from urls import urls


async def start_background_tasks(app: web.Application):
    """
    Establish database connection
    """
    app['db'] = await create_engine(**settings.DATABASE, loop=app.loop)


async def stop_background_tasks(app: web.Application):
    """
    Close database connection
    """
    app['db'].close()
    await app['db'].wait_closed()


def create_app(loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    if settings.DEBUG:
        aiohttp_autoreload.start()

    app = web.Application(
        middlewares=[
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
