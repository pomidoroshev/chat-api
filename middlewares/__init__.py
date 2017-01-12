from functools import wraps

__all__ = ['db']


async def db(app, handler):
    @wraps(handler)
    async def middleware_handler(request):
        async with app['db'].acquire() as conn:
            request['conn'] = conn
            result = await handler(request)

        return result

    return middleware_handler
