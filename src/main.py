from fastapi import FastAPI

from src.routes.home_route import router as home_router
from src.routes.auth_route import router as auth_router
from src.routes.bookmark_route import router as bookmark_router
from src.routes.redirect_route import router as redirect_router

app = FastAPI()

app.include_router(router=home_router)
app.include_router(router=auth_router)
app.include_router(router=bookmark_router)
app.include_router(router=redirect_router)
