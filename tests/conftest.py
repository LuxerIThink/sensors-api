import pytest
from fastapi.testclient import TestClient
from tortoise import Tortoise
from api.internal.authentication import Token
from api.main import app
from api.models import User


async def init_db() -> None:
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={
            "api": [
                "api.models",
            ]
        },
    )
    await Tortoise.generate_schemas()


@pytest.fixture(scope="session")
def client():
    client = TestClient(app)
    return client


@pytest.fixture(scope="function", autouse=True)
async def initialize_tests():
    await init_db()
    yield
    await Tortoise._drop_databases()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function")
def correct_user_data(client):
    return {
        "username": "username",
        "password": "Pa$Sw0rd",
        "email": "email@xyz.com",
    }


@pytest.fixture(scope="function")
async def correct_user(client, correct_user_data):
    return await User.create(**correct_user_data)


@pytest.fixture(scope="function")
async def correct_token(client, correct_user, correct_user_data):
    email = correct_user_data["email"]
    token_data = {"email": email}
    token = Token.encode_token(token_data)
    return f"bearer {token}"
