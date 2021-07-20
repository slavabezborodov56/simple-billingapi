import json
import os
import pkg_resources

from aiohttp import web


async def ping(request: web.Request) -> web.Response:
    """
    ---
    description: Метод позволяет проверить, что сервис запущен и работает.
    tags:
    - Health check
    produces:
    - application/json
    responses:
        "200":
            description: Диагностическая информация о запущенном сервисе.
    """
    return web.Response(
        content_type='application/json',
        body=json.dumps({
            'status': 'ok',
            'application': os.getenv('APPLICATION_NAME'),
            'version': pkg_resources.get_distribution('simple-billingapi').version,
        }),
    )
