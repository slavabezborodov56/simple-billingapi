from aiohttp.web import middleware, json_response
from aiohttp.web import Request, Response

from simple_billingapi.exceptions import BrokenRulesException


@middleware
async def request_id_middleware(request: Request, handler) -> Response:
    if not request.headers.get('X-Request-Id'):
        raise BrokenRulesException(message='Ожидается заголовок X-Request-Id')
    return await handler(request)


@middleware
async def broken_rules_middleware(request: Request, handler) -> Response:
    try:
        return await handler(request)
    except BrokenRulesException as exc:
        return json_response(
            status=400,
            data={
                'error': exc.message,
            },
        )
