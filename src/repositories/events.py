import typing as tp
import uuid
from datetime import datetime

from src.utils.olap import GetClickhouseConnection

__all__ = [
    "insert_content_event_repository",
    "insert_topic_event_repository",
]


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
                """
                INSERT INTO content_events
                (content_event_uuid, user_id, content, ts)
                VALUES
                """,
                [
                    (
                        str(content_event_uuid),
                        user_id,
                        content,
                        str(ts),
                    ),
                ],
            )


async def insert_topic_event_repository(
    keywords_names: tp.Sequence[str],
    keywords_weights: tp.Sequence[float],
    entities_categories: tp.Sequence[str],
    entities_names: tp.Sequence[str],
    entities_weights: tp.Sequence[float],
    sentiments_names: tp.Sequence[str],
    sentiments_weights: tp.Sequence[float],
    topic_event_uuid: uuid.UUID,
    content_event_uuid: uuid.UUID,
    user_id: str,
    ts: datetime,
    *,
    get_connection: GetClickhouseConnection,
) -> None:
    async with get_connection() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO topic_events
                    (topic_event_uuid, content_event_uuid, user_id,
                     sentiments.name, sentiments.weight,
                     keywords.name,   keywords.weight,
                     entities.category, entities.name, entities.weight,
                     ts)
                VALUES
                """,
                [
                    (
                        str(topic_event_uuid),
                        str(content_event_uuid),
                        user_id,
                        sentiments_names,
                        sentiments_weights,
                        keywords_names,
                        keywords_weights,
                        entities_categories,
                        entities_names,
                        entities_weights,
                        str(ts),
                    ),
                ],
            )
