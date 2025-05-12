import typing as tp

from fastapi import APIRouter, Body, Request, status

from src.api.transformers import (
    content_event_create_dto_to_content_event_broker_publish_dto_transformer,
)
from src.dtos import ContentEventCreateDTO, MessageResponseDTO

__all__ = ["router"]


router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.post(
    "/content/submitForProcessing",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=MessageResponseDTO,
)
async def submit_content_event_for_processing_endpoint(
    request: Request,
    body: tp.Annotated[ContentEventCreateDTO, Body()],
) -> tp.Any:
    await request.state.broker.publish(
        content_event_create_dto_to_content_event_broker_publish_dto_transformer(body),
        "events-content",
    )
    return MessageResponseDTO(message="Content event has been queued for creation")


@router.get(
    "/content",
    status_code=status.HTTP_200_OK,
    response_model=None,
)
async def get_content_events_endpoint(
    request: Request,
) -> tp.Any: ...


@router.get(
    "/topicAttributes",
    status_code=status.HTTP_200_OK,
    response_model=None,
)
async def get_topic_attributes_events_endpoint(
    request: Request,
) -> tp.Any: ...


@router.get(
    "/topicAttributes/{topic_attributes_event_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=None,
)
async def get_topic_attributes_event_endpoint(
    request: Request,
) -> tp.Any: ...
