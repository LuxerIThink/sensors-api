from tortoise import Tortoise
from .startup.orm import connect_to_db
from fastapi import FastAPI
from app.internal.exceptions_handlers import validation_exception_handler
from tortoise.exceptions import ValidationError
from jose import JWTError
from argon2.exceptions import VerifyMismatchError


app = FastAPI()
connect_to_db(app)
Tortoise.init_models(["app.models"], "app")

# WARNING! This import must be here because
# Pydantics must be initialized after Tortoise early init to
# correct work relations in Pydantics
from .routers import actions, users, devices

app.include_router(actions.router)
app.include_router(users.router)
app.include_router(devices.router)

app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(JWTError, validation_exception_handler)
app.add_exception_handler(VerifyMismatchError, validation_exception_handler)
