from faststream.kafka import KafkaRouter
from faststream.kafka.fastapi import Context
from starlette.datastructures import State

from src.dtos import TopicProfileDTO, TopicProfileEventBrokerDTO
from src.repositories import upsert_topic_profile_repository

__all__ = ["router"]


router = KafkaRouter()


@router.subscriber("topicProfile")
async def transmit_topic_profile_event_to_olap_handler(
    incoming_topic_profile_event: TopicProfileEventBrokerDTO,
    state: State = Context("state"),
) -> None:
    await upsert_topic_profile_repository(
        TopicProfileDTO(
            user_id=incoming_topic_profile_event.user_id,
            topics=incoming_topic_profile_event.topics,
        ).model_dump(),
        database=state.mongo_database,
    )
