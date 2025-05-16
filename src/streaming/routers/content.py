from faststream.kafka import KafkaRouter
from faststream.kafka.fastapi import Context
from starlette.datastructures import State

from src.dtos import ContentEventBrokerDTO
from src.repositories import insert_content_event_repository

__all__ = ["router"]


router = KafkaRouter()


@router.subscriber("contentEvent")
async def transmit_content_event_to_olap_handler(
    incoming_content_event: ContentEventBrokerDTO,
    state: State = Context("state"),
) -> None:
    await insert_content_event_repository(
        content_event_uuid=incoming_content_event.content_event_uuid,
        user_id=incoming_content_event.user_id,
        content=incoming_content_event.content,
        ts=incoming_content_event.timestamp,
        get_connection=state.get_clickhouse_connection,
    )
