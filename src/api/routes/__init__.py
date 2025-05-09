from fastapi import APIRouter

from .users import router as users_router

__all__ = ["router"]

router = APIRouter()
router.include_router(users_router)
