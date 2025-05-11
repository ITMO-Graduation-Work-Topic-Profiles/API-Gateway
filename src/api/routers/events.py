import typing as tp

from fastapi import APIRouter, Body, HTTPException, Request, status

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
    "/content",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=MessageResponseDTO,
)
async def create_content_event_endpoint(
    request: Request,
    body: tp.Annotated[ContentEventCreateDTO, Body()],
) -> tp.Any:
    # TODO: Get rid of try-except construction, it is necessary only for testing
    try:
        await request.state.broker.publish(
            content_event_create_dto_to_content_event_broker_publish_dto_transformer(
                body
            ),
            "events-content",
        )
        return MessageResponseDTO(message="Content event has been queued for creation")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to publish content event",
        )
