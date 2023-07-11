import pytest
from fastapi.testclient import TestClient
from tortoise import Tortoise

from api.main import app
from api.models.user import User


async def init_db() -> None:
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={'api': ['api.models', ]}
    )
    await Tortoise.generate_schemas()


@pytest.fixture(scope="session")
def client():
    client = TestClient(app)
    print("Client is ready")
    return client


@pytest.fixture(scope="session", autouse=True)
async def initialize_tests():
    await init_db()
    yield
    await Tortoise._drop_databases()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_testpost(client):  # Pass the client fixture as an argument
    username, password, email = ["luxer", "xyz12345", "xyz@xyz.pl"]

    assert await User.filter(username=username) == []

    data = {
        "username": username,
        "password": password,
        "email": email
    }
    encoded_data = data
    response = client.post(
        "/users/",
        json=encoded_data,
    )
    assert response.status_code == 200

    assert await User.filter(username=username).count() == 1
