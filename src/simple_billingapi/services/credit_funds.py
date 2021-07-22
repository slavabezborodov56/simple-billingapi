from contextlib import suppress
from datetime import datetime

import pytz
from asyncpg.exceptions import UniqueViolationError
from asyncpg.pool import Pool

from simple_billingapi.entities import CreditFundsDTO
from simple_billingapi.exceptions import BrokenRulesException
from simple_billingapi.repositories.postgres import log_write, user_add_funds


async def credit_funds(data: CreditFundsDTO, *, pool: Pool) -> None:
    if data.amount <= 0:
        raise BrokenRulesException(message='Можно зачислить только положительную сумму')

    async with pool.acquire() as connection:
        with suppress(UniqueViolationError):
            async with connection.transaction():
                user_wallet_id = await user_add_funds(
                    user_id=data.user_id,
                    amount=data.amount,
                    connection=connection,
                )
                await log_write(
                    wallet_from=None,
                    wallet_to=user_wallet_id,
                    amount=data.amount,
                    idempotency_key=data.idempotency_key,
                    now=datetime.now(pytz.utc),
                    connection=connection,
                )
