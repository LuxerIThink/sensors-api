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


@pytest.fixture(scope="session", autouse=True)
async def initialize_tests():
    await init_db()
    yield
    await Tortoise._drop_databases()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
