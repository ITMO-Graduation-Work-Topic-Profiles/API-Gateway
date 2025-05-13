import typing as tp

from src.dtos import ContentEventBrokerDTO, ContentEventCreateDTO
from src.dtos.events import UserContentEventDTO

__all__ = [
    "content_event_create_dto_to_content_event_broker_dto_transformer",
    "get_content_events_repository_to_user_content_event_dto_transformer",
]


def content_event_create_dto_to_content_event_broker_dto_transformer(
    dto: ContentEventCreateDTO,
) -> ContentEventBrokerDTO:
    return ContentEventBrokerDTO.model_validate(dto.model_dump())


def get_content_events_repository_to_user_content_event_dto_transformer(
    user_id: str,
    data: tp.Sequence[tp.Any],
) -> UserContentEventDTO:
    return UserContentEventDTO.model_validate(
        {
            "user_id": user_id,
            "content_events": data,
        }
    )
