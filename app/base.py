from fastapi import FastAPI, APIRouter
from .auth import route_user
from .expenses import route_expenses
from . import ui_routes
api_router = APIRouter()

api_router.include_router(route_user.router, prefix="", tags=["user management"])
api_router.include_router(route_expenses.router, prefix="", tags=["expense management"])
api_router.include_router(ui_routes.router, prefix="", tags=["ui"]) 

