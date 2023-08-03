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
def user_data(client):
    return {
        "username": "username",
        "password": "Pa$Sw0rd",
        "email": "email@xyz.com",
    }


@pytest.fixture(scope="function")
def create_user(client, user_data):
    response = client.post("/users/", json=user_data)
    return response.json()


@pytest.fixture(scope="function")
def create_header(client, create_user, user_data):
    login_data = user_data.copy()
    login_data.pop("email")
    header = {"Content-Type": "application/x-www-form-urlencoded"}
    response = client.post("/actions/token/", data=login_data, headers=header)
    data = response.json()
    token = f"{data['token_type']} {data['access_token']}"
    header = {"Authorization": token}
    return header
