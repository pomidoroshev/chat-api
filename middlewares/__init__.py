"""
App middlewares
"""
from functools import wraps

from utils import set_default_headers

__all__ = ['db', 'crossdomain']


async def db(app, handler):
    @wraps(handler)
    async def middleware_handler(request):
        async with app['db'].acquire() as conn:
            request['conn'] = conn
            result = await handler(request)

        return result

    return middleware_handler


async def crossdomain(app, handler):  # pylint: disable=unused-argument
    @wraps(handler)
    async def middleware_handler(request):
        response = await handler(request)
        set_default_headers(response.headers)
        return response

    return middleware_handler
