from tortoise import Tortoise
from .startup.orm import connect_to_db
from fastapi import FastAPI
from app.internal.exceptions_handlers import validation_exception_handler
from tortoise.exceptions import ValidationError
from jose import JWTError
from argon2.exceptions import VerifyMismatchError
from importlib import import_module


app = FastAPI()
connect_to_db(app)
Tortoise.init_models(["app.models"], "app")

app.include_router(import_module("app.routers.actions").router)
app.include_router(import_module("app.routers.users").router)
app.include_router(import_module("app.routers.devices").router)
app.include_router(import_module("app.routers.sensors").router)

app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(JWTError, validation_exception_handler)
app.add_exception_handler(VerifyMismatchError, validation_exception_handler)
