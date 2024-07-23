from typing import Annotated
from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction
from ..internal.authentication import authorize
from ..models.user import User
from ..pydantics.user import UserInPydantic, UserOutPydantic, UserInPydanticAllOptional

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
    return await User.create(**user.model_dump())


@router.put("/", response_model=UserOutPydantic)
async def edit_user(user_in: UserInPydanticAllOptional, uuid: Annotated[dict, Depends(authorize)]):
    async with in_transaction():
        user = await User.get(uuid=uuid)
        user_dict = user_in.model_dump(exclude_none=True, exclude_unset=True)
        await user.update_from_dict(user_dict).save(update_fields=user_dict)
    return user


@router.delete("/", response_model=UserOutPydantic)
async def remove_user(uuid: Annotated[dict, Depends(authorize)]):
    async with in_transaction():
        user = await User.get(uuid=uuid)
        await user.delete()
    return user
