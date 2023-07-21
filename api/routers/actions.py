from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from api.internal.authentication import get_token

router = APIRouter(
    prefix="/actions",
    tags=["actions"],
)


@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return await get_token(form_data.username, form_data.password)
