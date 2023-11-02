from typing import Annotated
from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction
from ..internal.authentication import authorize
from ..models.user import User
from ..pydantics.user import UserInPydantic, UserOutPydantic

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/", response_model=UserOutPydantic)
async def get_user(uuid: Annotated[dict, Depends(authorize)]):
    user = await User.get(uuid=uuid)
    return user


@router.post("/", response_model=UserOutPydantic)
async def create_user(user: UserInPydantic):
    return await User.create(**user.dict())


@router.put("/", response_model=UserOutPydantic)
async def edit_user(user_in: UserInPydantic, uuid: Annotated[dict, Depends(authorize)]):
    async with in_transaction():
        user = await User.get(uuid=uuid)
        await user.update_from_dict(user_in.dict()).save()
    return user


@router.delete("/")
async def remove_user(uuid: Annotated[dict, Depends(authorize)]):
    async with in_transaction():
        user = await User.get(uuid=uuid)
        await User.filter(uuid=uuid).delete()
    return user
