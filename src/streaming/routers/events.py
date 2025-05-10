from faststream.kafka import KafkaRouter
from faststream.kafka.fastapi import Context
from starlette.datastructures import State

from src.dtos import ContentEventBrokerDTO
from src.repositories import insert_content_event_repository

__all__ = ["router"]


router = KafkaRouter(prefix="events-")


@router.subscriber("content")
async def transmit_content_event_to_olap_handler(
    dto: ContentEventBrokerDTO,
    state: State = Context("state"),
) -> None:
    await insert_content_event_repository(
        dto.content_event_uuid,
        dto.user_id,
        dto.content,
        dto.timestamp,
        get_connection=state.get_clickhouse_connection,
    )


@router.subscriber("topic")
async def transmit_topic_event_to_oltp_handler(
    dto: ContentEventBrokerDTO,
    state: State = Context("state"),
) -> None:
    pass
