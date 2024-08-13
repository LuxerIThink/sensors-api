from typing import Annotated
from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction
from ..internal.authentication import authorize
from ..models.user import User
from ..pydantics.user import (
    UserInPydantic,
    UserOutPydantic,
    UserInPydanticAllOptional,
    UsersOutPydantic,
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/", response_model=UsersOutPydantic)
async def get_user(uuid: Annotated[dict, Depends(authorize)]):
    return await User.filter(uuid=uuid)


@router.post("/", response_model=UserOutPydantic)
async def create_user(user: UserInPydantic):
    return await User.create(**user.model_dump())


@router.put("/", response_model=UserOutPydantic)
async def edit_user(uuid: Annotated[dict, Depends(authorize)], user_in: UserInPydantic):
    user_dict = user_in.model_dump(exclude_none=True, exclude_unset=True)
    async with in_transaction():
        user = await User.get(uuid=uuid)
        await user.update_from_dict(user_dict).save(update_fields=user_dict.keys())
        return user


@router.patch("/", response_model=UserOutPydantic)
async def edit_partially_user(
    uuid: Annotated[dict, Depends(authorize)], user_in: UserInPydanticAllOptional
):
    user_dict = user_in.model_dump(exclude_none=True, exclude_unset=True)
    async with in_transaction():
        user = await User.get(uuid=uuid)
        await user.update_from_dict(user_dict).save(update_fields=user_dict.keys())
        return user


@router.delete("/", response_model=UserOutPydantic)
async def remove_user(uuid: Annotated[dict, Depends(authorize)]):
    async with in_transaction():
        user = await User.get(uuid=uuid)
        await user.delete()
        return user
