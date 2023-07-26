import pytest
from fastapi.testclient import TestClient
from tortoise import Tortoise

from api.main import app


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
async def correct_token(client):
    register_data = {
        "username": "username",
        "password": "Pa$Sw0rd",
        "email": "email@xyz.com",
    }
    client.post("/users/", json=register_data)
    login_data = {key: value for key, value in register_data.items() if key != "email"}
    header = {"Content-Type": "application/x-www-form-urlencoded"}

    response = client.post("/actions/token/", data=login_data, headers=header)
    output_data = response.json()

    token = f"{output_data['token_type']} {output_data['access_token']}"
    return token
