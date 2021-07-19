import json

from aiohttp import web


async def ping(request: web.Request) -> web.Response:
    return web.Response(
        content_type='application/json',
        body=json.dumps({'status': 'ok'}),
    )
