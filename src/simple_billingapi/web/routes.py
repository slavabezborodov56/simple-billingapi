from aiohttp import web

from . import handlers


routes = [
    web.get('/ping/', handlers.ping)
]