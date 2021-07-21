from aiohttp import web

from . import handlers


routes = [
    web.get('/ping/', handlers.ping, allow_head=False),

    web.post('/public/v1/create-user/', handlers.create_user_handler),
]
