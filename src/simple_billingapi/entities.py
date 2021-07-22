from dataclasses import dataclass
from uuid import UUID


@dataclass
class CreateUserDTO:
    phone: str
    """Телефон"""
    idempotency_key: UUID
    """Ключ идемпотентности"""


@dataclass
class CreditFundsDTO:
    user_id: int
    """ID пользователя"""
    amount: int
    """Сумма для зачисления"""
    idempotency_key: UUID
    """Ключ идемпотентности"""


@dataclass
class TransferFundsDTO:
    sender_user_id: int
    """ID пользователя, который отправляет средства"""
    receiver_user_id: int
    """ID пользователя, который получает средства"""
    amount: int
    """Сумма для зачисления"""
    idempotency_key: UUID
    """Ключ идемпотентности"""


@dataclass
class PgWallet:
    id: int
    """ID кошелька"""
    amount: int
    """Остаток средств"""
