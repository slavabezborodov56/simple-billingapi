from asyncpg.connection import Connection


async def create_wallet(amount, *, connection: Connection) -> int:
    query = """
    INSERT INTO wallets (amount) VALUES ($1)
    RETURNING id 
    """
    params = (amount,)
    new_wallet_id = await connection.fetchval(query, *params)
    return new_wallet_id


async def create_user(phone, wallet_id, *, connection: Connection) -> int:
    query = """
    INSERT INTO users (phone, wallet_id) VALUES ($1, $2)
    RETURNING id
    """
    params = (phone, wallet_id)
    new_user_id = await connection.fetchval(query, *params)
    return new_user_id
