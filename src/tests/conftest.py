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


def create_user(client, user_json):
    response = client.post("/users/", json=user_json)
    return response.json()


def create_header(client, user_json) -> dict[str, str]:
    auth_json = user_json.copy()
    auth_json.pop("email")
    login_header = {"Content-Type": "application/x-www-form-urlencoded"}
    response = client.post("/actions/token/", data=auth_json, headers=login_header)
    data = response.json()
    token = f"{data['token_type']} {data['access_token']}"
    header = {"Authorization": token}
    return header


@pytest.fixture(scope="session")
def client():
    client = TestClient(app)
    return client


@pytest.fixture(scope="function", autouse=True)
async def init_tests():
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
def user2_json():
    return {
        "username": "username2",
        "password": "Pa$Sw0rd",
        "email": "xyz@email.com",
    }


@pytest.fixture(scope="function")
def user(client, user_json):
    return create_user(client, user_json)


@pytest.fixture(scope="function")
def user2(client, user2_json):
    return create_user(client, user2_json)


@pytest.fixture(scope="function")
def header(client, user, user_json):
    return create_header(client, user_json)


@pytest.fixture(scope="function")
def header2(client, user2, user2_json):
    return create_header(client, user2_json)


@pytest.fixture(scope="session")
def device_json():
    return {
        "name": "test_device",
        "is_shared": False,
    }


@pytest.fixture(scope="session")
def device_json_shared():
    return {
        "name": "test_device",
        "is_shared": True,
    }


@pytest.fixture(scope="function")
def device(client, header, device_json):
    response = client.post("/devices/", headers=header, json=device_json)
    return response.json()


@pytest.fixture(scope="function")
def device_shared(client, header, device_json_shared):
    response = client.post("/devices/", headers=header, json=device_json_shared)
    return response.json()


@pytest.fixture(scope="session")
def sensor_json():
    return {
        "name": "test_sensor",
        "unit": "test_unit",
    }


@pytest.fixture(scope="session")
def sensor2_json():
    return {
        "name": "test_sensor2",
        "unit": "test_unit2",
    }


@pytest.fixture(scope="function")
def sensor(client, header, device, sensor_json):
    response = client.post(
        "/sensors/" + device["uuid"], headers=header, json=sensor_json
    )
    return response.json()


@pytest.fixture(scope="function")
def sensor_shared(client, header, device_shared, sensor_json):
    response = client.post(
        "/sensors/" + device_shared["uuid"], headers=header, json=sensor_json
    )
    return response.json()


@pytest.fixture(scope="function")
def sensor_shared2(client, header, device_shared, sensor2_json):
    response = client.post(
        "/sensors/" + device_shared["uuid"], headers=header, json=sensor2_json
    )
    return response.json()


@pytest.fixture(scope="session")
def measurement_json():
    return {
        "time": "2024-07-30T14:48:00Z",
        "value": 5.0,
    }


@pytest.fixture(scope="session")
def measurement2_json():
    return {
        "time": "2023-01-19T12:58:03Z",
        "value": 10.0,
    }


@pytest.fixture(scope="function")
def measurement(client, header, sensor, measurement_json):
    response = client.post(
        "/measurements/" + sensor["uuid"], headers=header, json=measurement_json
    )
    return response.json()


@pytest.fixture(scope="function")
def measurement_shared(client, header, sensor_shared, measurement_json):
    response = client.post(
        "/measurements/" + sensor_shared["uuid"], headers=header, json=measurement_json
    )
    return response.json()


@pytest.fixture(scope="function")
def measurement_shared2(client, header, sensor_shared, measurement2_json):
    response = client.post(
        "/measurements/" + sensor_shared["uuid"], headers=header, json=measurement2_json
    )
    return response.json()
