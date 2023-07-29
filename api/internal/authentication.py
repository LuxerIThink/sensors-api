from typing import Annotated
from jose import jwt
from os import getenv
from api.models import User
from fastapi import Depends


class JwtService:
    def __init__(self):
        self.salt = str(getenv("JWT_SECRET"))
        self.algorithm = "HS256"

    def encode_token(self, data: dict) -> str:
        return jwt.encode(data, self.salt, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict:
        return jwt.decode(token, self.salt, algorithms=[self.algorithm])


jwt_service = JwtService()


async def get_token(username, password):
    user = await authenticate_user(username, password)
    token_data = {"email": user.email}
    token = jwt_service.encode_token(token_data)
    json = {"access_token": token, "token_type": "bearer"}
    return json


async def authenticate_user(username: str, password: str):
    user = await User.get(username=username)
    password_hasher.verify(user.password, password)
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    decoded_json = jwt_service.decode_token(token)
    user = await User.get(email=decoded_json["email"])
    return user
