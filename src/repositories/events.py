import uuid
from datetime import datetime

from src.utils.olap import GetClickhouseConnection

__all__ = ["insert_content_event_repository"]


async def insert_content_event_repository(
    content_event_uuid: uuid.UUID,
    user_id: str,
    content: str,
    ts: datetime,
    *,
    get_connection: GetClickhouseConnection,
) -> None:
    async with get_connection() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO content_events"
                "(content_event_uuid, user_id, content, ts)"
                "VALUES",
                [
                    (
                        str(content_event_uuid),
                        user_id,
                        content,
                        str(ts),
                    ),
                ],
            )
