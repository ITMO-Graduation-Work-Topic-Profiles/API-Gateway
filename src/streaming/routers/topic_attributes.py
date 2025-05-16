from faststream.kafka import KafkaRouter
from faststream.kafka.fastapi import Context
from starlette.datastructures import State

from src.dtos import AggregatedTopicAttributesDTO, TopicAttributesEventBrokerDTO
from src.repositories import (
    get_aggregated_topic_attributes_repository,
    insert_topic_attributes_event_repository,
    upsert_aggregated_topic_attributes_repository,
)
from src.utils.aggregated_topic_attributes import (
    update_aggregated_topic_attributes_dto_based_on_topic_attributes_event_schema,
)
from src.utils.manipulations import split_attributes_from_items

__all__ = ["router"]


router = KafkaRouter()


@router.subscriber("topicAttributes")
async def transmit_topic_event_to_oltp_handler(
    incoming_topic_attributes_event: TopicAttributesEventBrokerDTO,
    state: State = Context("state"),
) -> None:
    existing_aggregated_topic_attributes = (
        await get_aggregated_topic_attributes_repository(
            user_id=incoming_topic_attributes_event.user_id,
            database=state.mongo_database,
        )
    )

    if not existing_aggregated_topic_attributes:
        old_aggregated_topic_attributes = AggregatedTopicAttributesDTO(
            user_id=incoming_topic_attributes_event.user_id
        )
    else:
        old_aggregated_topic_attributes = AggregatedTopicAttributesDTO.model_validate(
            existing_aggregated_topic_attributes
        )

    new_aggregated_topic_attributes = (
        update_aggregated_topic_attributes_dto_based_on_topic_attributes_event_schema(
            old_aggregated_topic_attributes,
            incoming_topic_attributes_event,
        )
    )

    await upsert_aggregated_topic_attributes_repository(
        new_aggregated_topic_attributes.model_dump(),
        database=state.mongo_database,
    )


@router.subscriber("topicAttributes", group_id="A")
async def transmit_topic_attributes_event_to_olap_handler(
    incoming_topic_attributes_event: TopicAttributesEventBrokerDTO,
    state: State = Context("state"),
) -> None:
    keywords_names, keywords_weights = split_attributes_from_items(
        incoming_topic_attributes_event.keywords,
        "name",
        "weight",
    )
    entities_categories, entities_names, entities_weights = split_attributes_from_items(
        incoming_topic_attributes_event.entities,
        "category",
        "name",
        "weight",
    )
    sentiments_names, sentiments_weights = split_attributes_from_items(
        incoming_topic_attributes_event.sentiments,
        "name",
        "weight",
    )
    await insert_topic_attributes_event_repository(
        keywords_names=keywords_names,
        keywords_weights=keywords_weights,
        entities_categories=entities_categories,
        entities_names=entities_names,
        entities_weights=entities_weights,
        sentiments_names=sentiments_names,
        sentiments_weights=sentiments_weights,
        topic_attributes_event_uuid=incoming_topic_attributes_event.topic_attributes_event_uuid,
        content_event_uuid=incoming_topic_attributes_event.content_event_uuid,
        user_id=incoming_topic_attributes_event.user_id,
        ts=incoming_topic_attributes_event.timestamp,
        get_connection=state.get_clickhouse_connection,
    )
