from contextlib import suppress
from datetime import datetime

import pytz
from asyncpg.exceptions import UniqueViolationError
from asyncpg.pool import Pool

from simple_billingapi.entities import CreditFundsDTO
from simple_billingapi.exceptions import BrokenRulesException
from simple_billingapi.repositories.postgres import log_write, wallet_add, wallet_get_for_update


async def credit_funds(data: CreditFundsDTO, *, pool: Pool) -> int:
    if data.amount <= 0:
        raise BrokenRulesException(message='Можно зачислить только положительную сумму')

    async with pool.acquire() as connection:
        try:
            async with connection.transaction():
                pg_wallet = await wallet_get_for_update(
                    user_id=data.user_id,
                    connection=connection,
                )
                if pg_wallet is None:
                    raise BrokenRulesException(message='Пользователь не найден')
                pg_updated_wallet = await wallet_add(
                    wallet_id=pg_wallet.id,
                    amount=data.amount,
                    connection=connection,
                )
                await log_write(
                    wallet_from=None,
                    wallet_to=pg_wallet.id,
                    amount=data.amount,
                    idempotency_key=data.idempotency_key,
                    now=datetime.now(pytz.utc),
                    connection=connection,
                )
                return pg_updated_wallet.amount
        except UniqueViolationError:
            return pg_wallet.amount
