from typing import Annotated

from fastapi import APIRouter, Depends

from api.internal.authentication import get_current_user
from ..models.user import UserOutPydantic, UserInPydantic, User


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/", response_model=UserOutPydantic)
async def get_user(user: Annotated[User, Depends(get_current_user)]):
    return user


@router.post("/", response_model=UserOutPydantic)
async def create_user(user: UserInPydantic):
    return await User.create(**user.dict())
