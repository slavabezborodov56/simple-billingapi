from contextlib import suppress
from datetime import datetime
from typing import Optional

import pytz
from asyncpg.exceptions import UniqueViolationError
from asyncpg.pool import Pool

from simple_billingapi.entities import CreateUserDTO
from simple_billingapi.repositories.postgres import user_create, wallet_create, log_write


async def create_user(data: CreateUserDTO, *, pool: Pool) -> Optional[int]:
    initial_amount = 0
    now = datetime.now(pytz.utc)
    async with pool.acquire() as connection:
        with suppress(UniqueViolationError):
            async with connection.transaction():
                new_wallet_id = await wallet_create(
                    amount=initial_amount,
                    connection=connection,
                )
                new_user_id = await user_create(
                    phone=int(data.phone[-11:]),
                    wallet_id=new_wallet_id,
                    now=now,
                    connection=connection,
                )
                await log_write(
                    wallet_from=None,
                    wallet_to=new_wallet_id,
                    amount=initial_amount,
                    idempotency_key=data.idempotency_key,
                    now=now,
                    connection=connection,
                )
                return new_user_id
