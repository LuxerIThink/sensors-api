from tortoise.contrib.fastapi import register_tortoise
from os import getenv
from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__)


def connect_to_db(app: FastAPI) -> None:
    host = str(getenv("DB_HOST") or "0.0.0.0")
    port = str(getenv("DB_PORT") or "5432")
    user = str(getenv("DB_USER"))
    password = str(getenv("DB_PASSWORD"))
    db = str(getenv("DB_NAME") or "postgres")
    logger.exception(f"host: {host}, port: {port}, user: {user}, password: {password}, db: {db}")
    register_tortoise(
        app,
        config={
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "host": host,
                        "port": port,
                        "user": user,
                        "password": password,
                        "database": db,
                    },
                }
            },
            "apps": {
                "app": {
                    "models": [
                        "app.models",
                    ],
                }
            },
        },
        generate_schemas=True,
        add_exception_handlers=True,
    )
