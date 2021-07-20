import asyncio
import os

import asyncpg
import click
from aiohttp import web
from aiohttp_swagger import setup_swagger

from simple_billingapi import setup
from simple_billingapi.web.routes import routes


async def on_startup(app: web.Application) -> None:
    app['postgres'] = await asyncpg.create_pool(os.getenv('POSTGRES_CONNECTION'))


async def on_shutdown(app: web.Application) -> None:
    await asyncio.wait_for(app['postgres'].close(), timeout=10)


@click.group()
def cli() -> None:
    setup()


@cli.command()
@click.option('--debug', is_flag=True)
@click.option('--host', type=str, default='127.0.0.1')
@click.option('--port', type=int, default=8000)
def serve(debug: bool, host: str, port: int) -> None:
    app = web.Application(debug=debug)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    app.add_routes(routes)
    setup_swagger(app)
    web.run_app(app, host=host, port=port)
