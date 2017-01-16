import datetime
import json

from aiohttp.hdrs import METH_ALL
from aiopg.sa.result import RowProxy


class JSONEncoder(json.JSONEncoder):

    def default(self, obj):  # pylint: disable=method-hidden
        if isinstance(obj, RowProxy):
            return dict(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')

        return json.JSONEncoder.default(self, obj)


def dumps(data):
    return json.dumps(data, ensure_ascii=False, cls=JSONEncoder)


def set_default_headers(headers):
    headers['Access-Control-Allow-Origin'] = '*'
    headers['Access-Control-Allow-Credentials'] = 'true'
    headers['Access-Control-Allow-Headers'] = (
        'Cache-control, '
        'Accept, '
        'X-auth-token, '
        'Content-type, '
        'WWW-Authenticate')
    headers['Access-Control-Allow-Methods'] = ','.join(METH_ALL)
