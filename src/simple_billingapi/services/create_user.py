from contextlib import suppress
from typing import Optional

from asyncpg.exceptions import UniqueViolationError
from asyncpg.pool import Pool

from simple_billingapi.entities import CreateUserDTO
from simple_billingapi.repositories import postgres


async def create_user(data: CreateUserDTO, *, pool: Pool) -> Optional[int]:
    async with pool.acquire() as connection:
        with suppress(UniqueViolationError):
            async with connection.transaction():
                new_wallet_id = await postgres.create_wallet(
                    amount=0,
                    connection=connection,
                )
                new_user_id = await postgres.create_user(
                    phone=int(data.phone[-11:]),
                    wallet_id=new_wallet_id,
                    connection=connection,
                )
                return new_user_id
