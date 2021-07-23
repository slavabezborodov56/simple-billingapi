import asyncio
import os

import asyncpg
import click
from aiohttp import web

from simple_billingapi import setup
from simple_billingapi.web.middlewares import broken_rules_middleware, request_id_middleware
from simple_billingapi.web.views.ping import PingView
from simple_billingapi.web.views.users import UserCreateView
from simple_billingapi.web.views.wallets import CreditFundsView, TransferFundsView


async def pg_cleanup_ctx(app: web.Application):
    app['postgres'] = await asyncpg.create_pool(os.getenv('POSTGRES_CONNECTION'))
    yield
    await asyncio.wait_for(app['postgres'].close(), timeout=10)


@click.group()
def cli() -> None:
    setup()


@cli.command()
@click.option('--debug', is_flag=True)
@click.option('--host', type=str, default='127.0.0.1')
@click.option('--port', type=int, default=8000)
def serve(debug: bool, host: str, port: int) -> None:
    app = web.Application(
        debug=debug,
        middlewares=[
            broken_rules_middleware,
            request_id_middleware,
        ],
    )
    app.router.add_view('/ping/', PingView)
    app.router.add_view('/public/v1/create-user/', UserCreateView)
    app.router.add_view('/public/v1/credit-funds/', CreditFundsView)
    app.router.add_view('/public/v1/transfer-funds/', TransferFundsView)
    app.cleanup_ctx.append(pg_cleanup_ctx)
    web.run_app(app, host=host, port=port)
