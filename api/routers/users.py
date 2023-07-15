from fastapi import APIRouter
from ..models.user import UserOutPydantic, UserInPydantic, User


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/", response_model=UserOutPydantic)
async def create_user(user: UserInPydantic):
    return await User.create(**user.dict())
