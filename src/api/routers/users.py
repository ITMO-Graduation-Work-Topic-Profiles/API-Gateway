import typing as tp

from fastapi import APIRouter, Depends, Query, Request
from fastapi_pagination import Page, Params

from src.api.dtos import UserGetDTO
from src.api.enums import SentimentEnum
from src.api.transformers import get_users_repository_to_user_get_dto_transformer
from src.repositories import get_users_repository

__all__ = ["router"]


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/", response_model=Page[UserGetDTO])
async def get_users_endpoint(
    request: Request,
    params: tp.Annotated[Params, Depends()],
    keywords: tp.Annotated[list[str] | None, Query()] = None,
    entities: tp.Annotated[list[str] | None, Query()] = None,
    sentiment: tp.Annotated[SentimentEnum | None, Query()] = None,
) -> tp.Any:
    return await get_users_repository(
        request.app.state.mongo_database,
        params,
        transformer=get_users_repository_to_user_get_dto_transformer,
        keywords=keywords,
        entities=entities,
        sentiment=sentiment.value if sentiment else None,
    )
