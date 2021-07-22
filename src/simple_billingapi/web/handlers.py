import json
import os
import pkg_resources

from aiohttp import web

from simple_billingapi.entities import CreateUserDTO, CreditFundsDTO, TransferFundsDTO
from simple_billingapi.services.create_user import create_user
from simple_billingapi.services.credit_funds import credit_funds
from simple_billingapi.services.transfer_funds import transfer_funds


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
      required: true
      schema:
        type: object
        required:
          - phone
          - idempotency_key
        properties:
          phone:
            type: string
            description: Мобильный телефон.
            example: \"+79194071066\"
          idempotency_key:
            type: string
            format: uuid
            example: \"515dcc4b-9f6d-43fb-83b4-7f256d1e7240\"
    responses:
        "200":
            description: Информация о новом пользователе.
    """
    data = await request.json()
    new_user_id = await create_user(
        CreateUserDTO(
            phone=data['phone'],
            idempotency_key=data['idempotency_key'],
        ),
        pool=request.app['postgres'],
    )
    return web.json_response({
        'new_user_id': new_user_id,
    })


async def credit_funds_handler(request: web.Request) -> web.Response:
    """
    ---
    summary: Метод начисляет сумму пользователю.
    tags:
    - Wallets
    consumes:
    - application/json
    produces:
    - application/json
    parameters:
    - in: body
      name: request
      required: true
      schema:
        type: object
        required:
          - user_id
          - amount
          - idempotency_key
        properties:
          user_id:
            type: integer
            description: ID пользователя, которому нужно начислить средства.
            example: 1
          amount:
            type: integer
            description: Сумма, которую требуется начислить.
            example: 10
          idempotency_key:
            type: string
            format: uuid
            example: \"786706b8-ed80-443a-80f6-ea1fa8cc1b51\"
    responses:
        "200":
            description: Успешная операция.
    """
    data = await request.json()
    await credit_funds(
        CreditFundsDTO(
            user_id=data['user_id'],
            amount=data['amount'],
            idempotency_key=data['idempotency_key'],
        ),
        pool=request.app['postgres'],
    )
    return web.json_response({})


async def transfer_funds_handler(request: web.Request) -> web.Response:
    """
    ---
    summary: Метод переводит средства от одного пользователя к другому.
    tags:
    - Wallets
    consumes:
    - application/json
    produces:
    - application/json
    parameters:
    - in: body
      name: request
      required: true
      schema:
        type: object
        required:
          - sender_user_id
          - receiver_user_id
          - amount
          - idempotency_key
        properties:
          sender_user_id:
            type: integer
            description: ID пользователя, который отправляет средства.
            example: 1
          receiver_user_id:
            type: integer
            description: ID пользователя, который получает средства.
            example: 2
          amount:
            type: integer
            description: Сумма для перевода.
            example: 10
          idempotency_key:
            type: string
            format: uuid
            example: \"d0dba15a-a8fb-4c20-863c-9c356a2dd7f8\"
    responses:
        "200":
            description: Успешная операция.
    """
    data = await request.json()
    await transfer_funds(
        TransferFundsDTO(
            sender_user_id=data['sender_user_id'],
            receiver_user_id=data['receiver_user_id'],
            amount=data['amount'],
            idempotency_key=data['idempotency_key'],
        ),
        pool=request.app['postgres'],
    )
    return web.json_response({})
