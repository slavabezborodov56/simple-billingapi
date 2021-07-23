from dataclasses import dataclass
from datetime import datetime

import pytz
from asyncpg.exceptions import UniqueViolationError
from asyncpg.pool import Pool

from simple_billingapi.entities import TransferFundsDTO
from simple_billingapi.exceptions import BrokenRulesException
from simple_billingapi.repositories.postgres import log_write, wallet_add, wallet_get_for_update


@dataclass
class TransferResult:
    sender_current_balance: int
    receiver_current_balance: int


async def transfer_funds(data: TransferFundsDTO, *, pool: Pool) -> TransferResult:
    if data.amount <= 0:
        raise BrokenRulesException(message='Можно перевести только положительную сумму')

    async with pool.acquire() as connection:
        try:
            async with connection.transaction():
                sender_pg_wallet = await wallet_get_for_update(
                    data.sender_user_id,
                    connection=connection,
                )
                if sender_pg_wallet is None:
                    raise BrokenRulesException(message='Отправитель не найден')
                receiver_pg_wallet = await wallet_get_for_update(
                    data.receiver_user_id,
                    connection=connection,
                )
                if receiver_pg_wallet is None:
                    raise BrokenRulesException(message='Получатель не найден')
                if sender_pg_wallet.amount < data.amount:
                    raise BrokenRulesException(message='Недостаточно средств')
                updated_sender_pg_wallet = await wallet_add(
                    wallet_id=sender_pg_wallet.id,
                    amount=-data.amount,
                    connection=connection,
                )
                updated_receiver_pg_wallet = await wallet_add(
                    wallet_id=receiver_pg_wallet.id,
                    amount=data.amount,
                    connection=connection,
                )
                await log_write(
                    wallet_from=sender_pg_wallet.id,
                    wallet_to=receiver_pg_wallet.id,
                    amount=data.amount,
                    idempotency_key=data.idempotency_key,
                    now=datetime.now(pytz.utc),
                    connection=connection,
                )
                return TransferResult(
                    sender_current_balance=updated_sender_pg_wallet.amount,
                    receiver_current_balance=updated_receiver_pg_wallet.amount
                )
        except UniqueViolationError:
            return TransferResult(
                sender_current_balance=sender_pg_wallet.amount,
                receiver_current_balance=receiver_pg_wallet.amount
            )
