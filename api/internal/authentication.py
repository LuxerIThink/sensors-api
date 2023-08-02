from typing import Annotated
from fastapi.security import OAuth2PasswordBearer as OAuth2
from jose import jwt
from os import getenv
from fastapi import Depends


class Token:
    salt: str = str(getenv("JWT_SECRET"))
    __algorithm: str = "HS256"

    @classmethod
    def encode_token(cls, data: dict) -> str:
        return jwt.encode(data, cls.salt, algorithm=cls.__algorithm)

    @classmethod
    def decode_token(cls, token: str) -> dict:
        return jwt.decode(token, cls.salt, algorithms=[cls.__algorithm])


async def authorize(token: Annotated[str, Depends(OAuth2(tokenUrl="actions/token"))]):
    token_data = Token.decode_token(token)
    return token_data["uuid"]
