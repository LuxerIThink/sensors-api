from argon2 import PasswordHasher
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from app.internal.authentication import Token
from app.models import User

router = APIRouter(
    prefix="/actions",
    tags=["actions"],
)


@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await User.get(username=form_data.username)
    password_hasher = PasswordHasher()
    password_hasher.verify(user.password, form_data.password)
    data = {"uuid": str(user.uuid)}
    token = Token.encode_token(data)
    token_json = {"token_type": "bearer", "access_token": token}
    return token_json
