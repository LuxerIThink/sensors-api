from tortoise.contrib.fastapi import register_tortoise
from os import getenv
from fastapi import FastAPI


def connect_to_db(app: FastAPI) -> None:
    register_tortoise(
        app,
        config={
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "host": str(getenv("DB_HOST")),
                        "port": str(getenv("DB_PORT")),
                        "user": str(getenv("DB_USER")),
                        "password": str(getenv("DB_PASSWORD")),
                        "database": str(getenv("DB_NAME")),
                    },
                }
            },
            "apps": {
                "api": {
                    "models": [
                        "api.models",
                    ],
                }
            },
        },
        generate_schemas=True,
        add_exception_handlers=True,
    )
