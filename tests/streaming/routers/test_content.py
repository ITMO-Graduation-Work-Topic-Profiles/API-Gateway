import uuid
from unittest.mock import AsyncMock, patch

import pytest
from starlette.datastructures import State

from src.dtos import ContentEventBrokerDTO
from src.streaming.routers.content import transmit_content_event_to_olap_handler
from src.utils.dates import utcnow


class TestTransmitContentEventToOlapHandler:
    @pytest.mark.asyncio
    @patch("src.streaming.routers.content.insert_content_event_repository")
    async def test_transmit_content_event_to_olap_handler_success(
        self, mock_insert_content_event: AsyncMock
    ) -> None:
        # Arrange
        content_event_uuid = uuid.uuid4()
        user_id = "test_user_id"
        content = "Test content"
        timestamp = utcnow()

        content_event = ContentEventBrokerDTO(
            content_event_uuid=content_event_uuid,
            user_id=user_id,
            content=content,
            timestamp=timestamp,
        )

        mock_get_clickhouse_connection = AsyncMock()
        state = State()
        state.get_clickhouse_connection = mock_get_clickhouse_connection

        # Act
        await transmit_content_event_to_olap_handler(
            content_event,
            state=state,
        )

        # Assert
        mock_insert_content_event.assert_called_once_with(
            content_event_uuid=content_event_uuid,
            user_id=user_id,
            content=content,
            ts=timestamp,
            get_connection=mock_get_clickhouse_connection,
        )

    @pytest.mark.asyncio
    @patch("src.streaming.routers.content.insert_content_event_repository")
    async def test_transmit_content_event_to_olap_handler_error(
        self, mock_insert_content_event: AsyncMock
    ) -> None:
        # Arrange
        content_event = ContentEventBrokerDTO(
            content_event_uuid=uuid.uuid4(),
            user_id="test_user_id",
            content="Test content",
            timestamp=utcnow(),
        )

        mock_get_clickhouse_connection = AsyncMock()
        state = State()
        state.get_clickhouse_connection = mock_get_clickhouse_connection

        mock_insert_content_event.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await transmit_content_event_to_olap_handler(
                content_event,
                state=state,
            )

        mock_insert_content_event.assert_called_once()
