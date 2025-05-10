from src.api.dtos import ContentEventBrokerDTO, ContentEventCreateDTO

__all__ = ["content_event_create_dto_to_content_event_broker_publish_dto_transformer"]


def content_event_create_dto_to_content_event_broker_publish_dto_transformer(
    dto: ContentEventCreateDTO,
) -> ContentEventBrokerDTO:
    return ContentEventBrokerDTO.model_validate(dto.model_dump())
