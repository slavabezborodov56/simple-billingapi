from contextlib import suppress
from datetime import datetime

import pytz
from asyncpg.exceptions import UniqueViolationError
from asyncpg.pool import Pool

from simple_billingapi.entities import CreditFundsDTO, TransferFundsDTO
from simple_billingapi.exceptions import BrokenRulesException
from simple_billingapi.repositories.postgres import log_write, user_add_funds, wallet_get_for_update


async def transfer_funds(data: TransferFundsDTO, *, pool: Pool) -> None:
    if data.amount <= 0:
        raise BrokenRulesException(message='Можно перевести только положительную сумму')

    async with pool.acquire() as connection:
        with suppress(UniqueViolationError):
            async with connection.transaction():
                sender = await wallet_get_for_update(
                    data.sender_user_id,
                    connection=connection,
                )
                if sender.amount < data.amount:
                    raise BrokenRulesException(message='Недостаточно средств')
                sender_wallet_id = await user_add_funds(
                    user_id=data.sender_user_id,
                    amount=-data.amount,
                    connection=connection,
                )
                receiver_wallet_id = await user_add_funds(
                    user_id=data.receiver_user_id,
                    amount=data.amount,
                    connection=connection,
                )
                await log_write(
                    wallet_from=sender_wallet_id,
                    wallet_to=receiver_wallet_id,
                    amount=data.amount,
                    idempotency_key=data.idempotency_key,
                    now=datetime.now(pytz.utc),
                    connection=connection,
                )
