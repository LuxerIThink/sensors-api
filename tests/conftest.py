import pytest
from fastapi.testclient import TestClient
from tortoise import Tortoise
from app.main import app


async def init_db() -> None:
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={
            "app": [
                "app.models",
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


@pytest.fixture(scope="session")
def user_json():
    return {
        "username": "username",
        "password": "Pa$Sw0rd",
        "email": "email@xyz.com",
    }


@pytest.fixture(scope="session")
def auth_json(user_json):
    auth_json = user_json.copy()
    auth_json.pop("email")
    return auth_json


@pytest.fixture(scope="function")
def user(client, user_json):
    response = client.post("/users/", json=user_json)
    return response.json()


@pytest.fixture(scope="function")
def auth_header(client, user, auth_json, user_json):
    header = {"Content-Type": "application/x-www-form-urlencoded"}
    response = client.post("/actions/token/", data=auth_json, headers=header)
    data = response.json()
    token = f"{data['token_type']} {data['access_token']}"
    header = {"Authorization": token}
    return header


@pytest.fixture(scope="session")
def device_json():
    return {
        "name": "test_device",
        "is_shared": True,
    }


@pytest.fixture(scope="function")
def device(client, auth_header, device_json):
    response = client.post("/devices/", headers=auth_header, json=device_json)
    return response.json()


@pytest.fixture(scope="session")
def sensor_json():
    return {
        "name": "test_sensor",
        "unit": "test_unit",
    }


@pytest.fixture(scope="function")
def sensor(client, auth_header, device, sensor_json):
    response = client.post("/sensors/" + device["uuid"], headers=auth_header, json=sensor_json)
    return response.json()

