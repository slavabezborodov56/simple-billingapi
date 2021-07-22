from datetime import datetime
from typing import Optional
from uuid import UUID

from asyncpg.connection import Connection

from simple_billingapi.entities import PgWallet


async def wallet_create(amount: int, *, connection: Connection) -> int:
    query = """
    INSERT INTO wallets (amount) VALUES ($1)
    RETURNING id 
    """
    params = (amount,)
    new_wallet_id = await connection.fetchval(query, *params)
    return new_wallet_id


async def wallet_get_for_update(user_id: int, *, connection: Connection) -> Optional[PgWallet]:
    query = """
    SELECT id, amount FROM wallets WHERE id = (
        SELECT wallet_id FROM users WHERE users.id = $1
    ) FOR UPDATE 
    """
    params = (user_id,)
    if row := await connection.fetchrow(query, *params):
        return PgWallet(
            id=row['id'],
            amount=row['amount'],
        )


async def user_create(phone: int, wallet_id: int, now: datetime, *, connection: Connection) -> int:
    query = """
    INSERT INTO users (phone, wallet_id, created_at) VALUES ($1, $2, $3)
    RETURNING id
    """
    params = (phone, wallet_id, now)
    new_user_id = await connection.fetchval(query, *params)
    return new_user_id


async def user_add_funds(user_id: int, amount: int, *, connection: Connection) -> Optional[int]:
    query = """
    UPDATE wallets SET amount = amount + $1 WHERE id = (
        SELECT wallet_id FROM users WHERE users.id = $2
    )
    RETURNING wallets.id
    """
    params = (amount, user_id)
    return await connection.fetchval(query, *params)


async def log_write(
        wallet_from: Optional[int],
        wallet_to: int,
        amount: int,
        idempotency_key: UUID,
        now: datetime,
        *,
        connection: Connection,
) -> None:
    query = """
    INSERT INTO operation_logs (wallet_from, wallet_to, amount, idempotency_key, date)
    VALUES ($1, $2, $3, $4, $5)
    """
    params = (wallet_from, wallet_to, amount, idempotency_key, now)
    await connection.execute(query, *params)
