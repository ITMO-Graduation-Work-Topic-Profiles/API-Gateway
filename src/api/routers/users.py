import typing as tp

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Path,
    Query,
    Request,
    status,
)
from fastapi_pagination import Page, Params

from src.api.transformers import (
    get_content_events_repository_to_user_content_event_dto_transformer,
    get_user_with_topic_info_repository_to_user_get_dto_transformer,
    get_users_with_topic_info_paginated_repository_to_user_get_dto_transformer,
)
from src.dtos import MessageResponseDTO, UserCreateDTO, UserGetDTO
from src.repositories import (
    get_content_events_repository,
    get_user_with_topic_info_repository,
    get_users_with_topic_info_paginated_repository,
    insert_user_repository,
)

__all__ = ["router"]


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Page[UserGetDTO],
)
async def get_users_with_topic_info_endpoint(
    request: Request,
    params: tp.Annotated[Params, Depends()],
    keywords: tp.Annotated[tp.Sequence[str] | None, Query()] = None,
    entities: tp.Annotated[tp.Sequence[str] | None, Query()] = None,
    sentiments: tp.Annotated[tp.Sequence[str] | None, Query()] = None,
) -> tp.Any:
    return await get_users_with_topic_info_paginated_repository(
        keywords=keywords or [],
        entities=entities or [],
        sentiments=sentiments or [],
        params=params,
        transformer=get_users_with_topic_info_paginated_repository_to_user_get_dto_transformer,
        database=request.app.state.mongo_database,
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=UserGetDTO,
)
async def create_user_endpoint(
    request: Request,
    body: tp.Annotated[UserCreateDTO, Body()],
) -> tp.Any:
    existing_user = await get_user_with_topic_info_repository(
        user_id=body.user_id,
        database=request.app.state.mongo_database,
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with user_id {body.user_id} already exists",
        )

    await insert_user_repository(
        data=body.model_dump(),
        database=request.app.state.mongo_database,
    )
    user = await get_user_with_topic_info_repository(
        user_id=body.user_id,
        database=request.app.state.mongo_database,
    )

    return get_user_with_topic_info_repository_to_user_get_dto_transformer(user)


@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserGetDTO,
)
async def get_user_by_id_endpoint(
    request: Request,
    user_id: tp.Annotated[str, Path()],
) -> tp.Any:
    user = await get_user_with_topic_info_repository(
        user_id=user_id,
        database=request.app.state.mongo_database,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with user_id {user_id} not found",
        )

    return get_user_with_topic_info_repository_to_user_get_dto_transformer(user)


@router.post(
    "/{user_id}/topicProfile/submitForProcessing",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=MessageResponseDTO,
)
async def submit_topic_profile_for_processing_endpoint(
    request: Request,
    user_id: tp.Annotated[str, Path()],
) -> tp.Any:
    content_events = await get_content_events_repository(
        user_id,
        get_connection=request.app.state.get_clickhouse_connection,
    )
    user_content_event = (
        get_content_events_repository_to_user_content_event_dto_transformer(
            user_id,
            content_events,
        )
    )
    await request.state.broker.publish(
        user_content_event.model_dump(),
        "userContent",
    )

    return MessageResponseDTO(message="Topic profile has been queued for creation")
