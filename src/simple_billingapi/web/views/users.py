from uuid import UUID

from aiohttp_pydantic import PydanticView
from pydantic import BaseModel
from aiohttp.web import json_response

from simple_billingapi.entities import CreateUserDTO
from simple_billingapi.services.create_user import create_user


class UserCreateModel(BaseModel):
    phone: str


class UserCreateView(PydanticView):
    async def post(self, user: UserCreateModel, *, idempotency_key: UUID):
        created_user_id = await create_user(
            CreateUserDTO(
                phone=user.phone,
                idempotency_key=idempotency_key,
            ),
            pool=self.request.app['postgres'],
        )
        return json_response({
            'created_user_id': created_user_id,
        })
