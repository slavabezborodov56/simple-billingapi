import json
import os
import pkg_resources

from aiohttp import web

from simple_billingapi.entities import CreateUserDTO
from simple_billingapi.services.create_user import create_user


async def ping(request: web.Request) -> web.Response:
    """
    ---
    summary: Метод позволяет проверить, что сервис запущен и работает.
    tags:
    - Health check
    produces:
    - application/json
    responses:
        "200":
            description: Данные о запущенном сервисе.
    """
    return web.json_response({
        'status': 'ok',
        'application': os.getenv('APPLICATION_NAME'),
        'version': pkg_resources.get_distribution('simple-billingapi').version,
    })


async def create_user_handler(request: web.Request) -> web.Response:
    """
    ---
    summary: Метод создает нового пользователя с нулевым балансом.
    tags:
    - Users
    consumes:
    - application/json
    produces:
    - application/json
    parameters:
    - in: body
      name: request
      description: Мобильный телефон.
      required: true
      schema:
        type: object
        required:
          - phone
        properties:
          phone:
            type: string
            example: \"+79194071066\"
    responses:
        "200":
            description: Информация о новом пользователе.
    """
    data = await request.json()
    new_user_id = await create_user(
        CreateUserDTO(
            phone=data['phone'],
        ),
        pool=request.app['postgres'],
    )
    return web.json_response({
        'new_user_id': new_user_id,
    })
