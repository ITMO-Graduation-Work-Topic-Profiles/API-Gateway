from fastapi import APIRouter

from .users import router as users_router

__all__ = ["api_router"]

api_router = APIRouter()
api_router.include_router(users_router)
