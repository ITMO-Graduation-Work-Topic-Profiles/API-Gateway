from faststream.kafka import KafkaRouter
from faststream.kafka.fastapi import Context
from starlette.datastructures import State

from src.dtos import ContentEventBrokerDTO, TopicProfileDTO
from src.dtos.events import TopicEventBrokerDTO
from src.repositories import insert_content_event_repository

__all__ = ["router"]

from src.repositories.topic_proflies import (
    get_topic_profile_repository,
    upsert_topic_profile_repository,
)
from src.schemas import TopicAttributesSchema
from src.utils.topic_profiles import (
    update_topic_attributes_schema_based_on_topic_event_schema,
)

router = KafkaRouter(prefix="events-")


@router.subscriber("content")
async def transmit_content_event_to_olap_handler(
    incoming_content_event: ContentEventBrokerDTO,
    state: State = Context("state"),
) -> None:
    await insert_content_event_repository(
        incoming_content_event.content_event_uuid,
        incoming_content_event.user_id,
        incoming_content_event.content,
        incoming_content_event.timestamp,
        get_connection=state.get_clickhouse_connection,
    )


@router.subscriber("topic")
async def transmit_topic_event_to_oltp_handler(
    incoming_topic_event: TopicEventBrokerDTO,
    state: State = Context("state"),
) -> None:
    existing_topic_profile = await get_topic_profile_repository(
        incoming_topic_event.user_id,
        database=state.mongo_database,
    )

    if not existing_topic_profile:
        old_topic_attributes = TopicAttributesSchema()
    else:
        old_topic_attributes = TopicAttributesSchema.model_validate(
            existing_topic_profile["topic_attributes"]
        )

    new_topic_attributes = update_topic_attributes_schema_based_on_topic_event_schema(
        old_topic_attributes,
        incoming_topic_event,
    )

    await upsert_topic_profile_repository(
        TopicProfileDTO(
            user_id=incoming_topic_event.user_id,
            topic_attributes=new_topic_attributes,
        ).model_dump(),
        database=state.mongo_database,
    )
