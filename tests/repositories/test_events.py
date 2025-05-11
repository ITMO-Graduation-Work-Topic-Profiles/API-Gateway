import typing as tp
import uuid
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.repositories.events import (
    insert_content_event_repository,
    insert_topic_event_repository,
)
from src.utils.dates import utcnow


def create_mock_connection_factory(
    connection: MagicMock | None = None, error: Exception | None = None
) -> tp.Callable[[], tp.AsyncContextManager[MagicMock]]:
    @asynccontextmanager
    async def mock_get_connection() -> tp.AsyncIterator[MagicMock]:
        if error:
            raise error
        yield connection if connection is not None else MagicMock()

    return mock_get_connection


class TestInsertContentEventRepository:
    @pytest.mark.asyncio
    async def test_insert_content_event_repository_success(self) -> None:
        content_event_uuid = uuid.uuid4()
        user_id = "test_user_id"
        content = "Test content"
        ts = utcnow()

        mock_cursor = AsyncMock()
        mock_connection = MagicMock()

        @asynccontextmanager
        async def mock_cursor_cm() -> tp.AsyncIterator[AsyncMock]:
            yield mock_cursor

        mock_connection.cursor = mock_cursor_cm

        mock_get_connection = create_mock_connection_factory(connection=mock_connection)

        await insert_content_event_repository(
            content_event_uuid=content_event_uuid,
            user_id=user_id,
            content=content,
            ts=ts,
            get_connection=mock_get_connection,
        )

        mock_cursor.execute.assert_called_once()

        sql, params = mock_cursor.execute.call_args.args
        assert "INSERT INTO content_events" in sql
        assert "(content_event_uuid, user_id, content, ts)" in sql
        assert "VALUES" in sql

        assert len(params) == 1
        row = params[0]
        assert row[0] == str(content_event_uuid)
        assert row[1] == user_id
        assert row[2] == content
        assert row[3] == str(ts)

    @pytest.mark.asyncio
    async def test_insert_content_event_repository_connection_error(self) -> None:
        content_event_uuid = uuid.uuid4()
        user_id = "test_user_id"
        content = "Test content"
        ts = utcnow()

        mock_get_connection = create_mock_connection_factory(
            error=Exception("Connection error")
        )

        with pytest.raises(Exception, match="Connection error"):
            await insert_content_event_repository(
                content_event_uuid=content_event_uuid,
                user_id=user_id,
                content=content,
                ts=ts,
                get_connection=mock_get_connection,
            )


class TestInsertTopicEventRepository:
    @pytest.mark.asyncio
    async def test_insert_topic_event_repository_success(self) -> None:
        keywords_names = ["python", "fastapi"]
        keywords_weights = [0.8, 0.7]
        entities_categories = ["language", "framework"]
        entities_names = ["python", "fastapi"]
        entities_weights = [0.8, 0.7]
        sentiments_names = ["positive", "neutral"]
        sentiments_weights = [0.9, 0.1]
        topic_event_uuid = uuid.uuid4()
        content_event_uuid = uuid.uuid4()
        user_id = "test_user_id"
        ts = utcnow()

        mock_cursor = AsyncMock()
        mock_connection = MagicMock()

        @asynccontextmanager
        async def mock_cursor_cm() -> tp.AsyncIterator[AsyncMock]:
            yield mock_cursor

        mock_connection.cursor = mock_cursor_cm

        mock_get_connection = create_mock_connection_factory(connection=mock_connection)

        await insert_topic_event_repository(
            keywords_names=keywords_names,
            keywords_weights=keywords_weights,
            entities_categories=entities_categories,
            entities_names=entities_names,
            entities_weights=entities_weights,
            sentiments_names=sentiments_names,
            sentiments_weights=sentiments_weights,
            topic_event_uuid=topic_event_uuid,
            content_event_uuid=content_event_uuid,
            user_id=user_id,
            ts=ts,
            get_connection=mock_get_connection,
        )

        mock_cursor.execute.assert_called_once()

        sql, params = mock_cursor.execute.call_args.args
        assert "INSERT INTO topic_events" in sql
        assert "topic_event_uuid, content_event_uuid, user_id" in sql
        assert "sentiments.name" in sql
        assert "sentiments.weight" in sql
        assert "keywords.name" in sql
        assert "keywords.weight" in sql
        assert "entities.category" in sql
        assert "entities.name" in sql
        assert "entities.weight" in sql
        assert "VALUES" in sql

        assert len(params) == 1
        row = params[0]
        assert row[0] == str(topic_event_uuid)
        assert row[1] == str(content_event_uuid)
        assert row[2] == user_id
        assert row[3] == sentiments_names
        assert row[4] == sentiments_weights
        assert row[5] == keywords_names
        assert row[6] == keywords_weights
        assert row[7] == entities_categories
        assert row[8] == entities_names
        assert row[9] == entities_weights
        assert row[10] == str(ts)

    @pytest.mark.asyncio
    async def test_insert_topic_event_repository_connection_error(self) -> None:
        keywords_names = ["python", "fastapi"]
        keywords_weights = [0.8, 0.7]
        entities_categories = ["language", "framework"]
        entities_names = ["python", "fastapi"]
        entities_weights = [0.8, 0.7]
        sentiments_names = ["positive", "neutral"]
        sentiments_weights = [0.9, 0.1]
        topic_event_uuid = uuid.uuid4()
        content_event_uuid = uuid.uuid4()
        user_id = "test_user_id"
        ts = utcnow()

        mock_get_connection = create_mock_connection_factory(
            error=Exception("Connection error")
        )

        with pytest.raises(Exception, match="Connection error"):
            await insert_topic_event_repository(
                keywords_names=keywords_names,
                keywords_weights=keywords_weights,
                entities_categories=entities_categories,
                entities_names=entities_names,
                entities_weights=entities_weights,
                sentiments_names=sentiments_names,
                sentiments_weights=sentiments_weights,
                topic_event_uuid=topic_event_uuid,
                content_event_uuid=content_event_uuid,
                user_id=user_id,
                ts=ts,
                get_connection=mock_get_connection,
            )
