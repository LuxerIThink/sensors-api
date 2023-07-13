from fastapi import FastAPI

from utils.exceptions_handlers import validation_exception_handler
from .routers import actions, users
from .startup.orm import connect_to_db
from tortoise.exceptions import ValidationError


app = FastAPI()

connect_to_db(app)

app.include_router(actions.router)
app.include_router(users.router)

app.add_exception_handler(ValidationError, validation_exception_handler)
