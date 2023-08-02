from typing import Annotated
from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction
from ..internal.authentication import authorize
from ..models.user import UserOutPydantic, UserInPydantic, User


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
async def edit_user(user: UserInPydantic, uuid: Annotated[dict, Depends(authorize)]):
    async with in_transaction():
        await User.filter(uuid=uuid).update(**user.dict())
        user_new = await User.get(uuid=uuid)
    return user_new


@router.delete("/")
async def remove_user(uuid: Annotated[dict, Depends(authorize)]):
    return await User.filter(uuid=uuid).delete()
