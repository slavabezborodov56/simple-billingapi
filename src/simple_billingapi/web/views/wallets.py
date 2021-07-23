from uuid import UUID

from aiohttp.web import json_response
from aiohttp_pydantic import PydanticView
from pydantic import BaseModel

from simple_billingapi.entities import CreditFundsDTO, TransferFundsDTO
from simple_billingapi.services.credit_funds import credit_funds
from simple_billingapi.services.transfer_funds import transfer_funds


class CreditFundsModel(BaseModel):
    user_id: int
    amount: int


class TransferFundsModel(BaseModel):
    sender_user_id: int
    receiver_user_id: int
    amount: int


class CreditFundsView(PydanticView):
    async def post(self, data: CreditFundsModel, *, idempotency_key: UUID):
        current_amount = await credit_funds(
            CreditFundsDTO(
                user_id=data.user_id,
                amount=data.amount,
                idempotency_key=idempotency_key,
            ),
            pool=self.request.app['postgres'],
        )
        return json_response({
            'current_amount': current_amount,
        })


class TransferFundsView(PydanticView):
    async def post(self, data: TransferFundsModel, *, idempotency_key: UUID):
        transfer_result = await transfer_funds(
            TransferFundsDTO(
                sender_user_id=data.sender_user_id,
                receiver_user_id=data.receiver_user_id,
                amount=data.amount,
                idempotency_key=idempotency_key,
            ),
            pool=self.request.app['postgres'],
        )
        return json_response({
            'sender_current_balance': transfer_result.sender_current_balance,
            'receiver_current_balance': transfer_result.receiver_current_balance,
        })
