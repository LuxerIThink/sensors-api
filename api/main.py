from fastapi import FastAPI
from .routers import actions

app = FastAPI()

app.include_router(actions.router)
