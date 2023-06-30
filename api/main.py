from fastapi import FastAPI
from .routers import actions
from .startup.orm import connect_to_db

app = FastAPI()

connect_to_db(app)

app.include_router(actions.router)
