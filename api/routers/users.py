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
async def get_user(token_data: Annotated[dict, Depends(authorize)]):
    user = await User.get(email=token_data["email"])
    return user


@router.post("/", response_model=UserOutPydantic)
async def create_user(user: UserInPydantic):
    return await User.create(**user.dict())


@router.put("/", response_model=UserOutPydantic)
async def edit_user(user: UserInPydantic, token: Annotated[dict, Depends(authorize)]):
    async with in_transaction():
        await User.filter(email=token["email"]).update(**user.dict())
        user_new = await User.get(email=user.dict()["email"])
    return user_new


@router.delete("/")
async def remove_user(token_data: Annotated[dict, Depends(authorize)]):
    return await User.filter(email=token_data["email"]).delete()
