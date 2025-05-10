import typing as tp

from fastapi import APIRouter, Body, Request

from src.api.dtos import ContentEventCreateDTO, MessageResponseDTO
from src.api.transformers import (
    content_event_create_dto_to_content_event_broker_publish_dto_transformer,
)

__all__ = ["router"]


router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.post("/content", response_model=MessageResponseDTO)
async def create_content_event_endpoint(
    request: Request,
    body: tp.Annotated[ContentEventCreateDTO, Body()],
) -> tp.Any:
    await request.state.broker.publish(
        content_event_create_dto_to_content_event_broker_publish_dto_transformer(body),
        "events-content",
    )
    return MessageResponseDTO(message="Event created successfully")
