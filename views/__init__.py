from aiohttp import web
from aiohttp.hdrs import METH_ALL


class BaseView(web.View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = self.request['conn']

    async def options(self):
        method = (x.upper() for x in dir(self) if x.upper() in METH_ALL)
        resp = web.HTTPOk()
        resp.headers['Allow'] = ','.join(method)

        return resp
