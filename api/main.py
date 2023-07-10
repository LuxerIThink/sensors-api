from fastapi import FastAPI
from .routers import actions, users
from .startup.orm import connect_to_db

app = FastAPI()

connect_to_db(app)

app.include_router(actions.router)
app.include_router(users.router)