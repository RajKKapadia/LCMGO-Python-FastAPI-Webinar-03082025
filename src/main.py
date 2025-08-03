from fastapi import FastAPI

from src.routes.home_route import router as home_router
from src.routes.auth_route import router as auth_router

app = FastAPI()

app.include_router(router=home_router)
app.include_router(router=auth_router)
