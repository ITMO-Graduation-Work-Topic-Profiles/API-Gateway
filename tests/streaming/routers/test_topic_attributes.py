import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.datastructures import State

from src.dtos import AggregatedTopicAttributesDTO, TopicAttributesEventBrokerDTO
from src.schemas import (
    EntityTopicEventSchema,
    KeywordTopicEventSchema,
    SentimentTopicEventSchema,
)
from src.streaming.routers.topic_attributes import (
    transmit_topic_attributes_event_to_olap_handler,
    transmit_topic_event_to_oltp_handler,
)
from src.utils.dates import utcnow


class TestTransmitTopicEventToOltpHandler:
    @pytest.mark.asyncio
    @patch(
        "src.streaming.routers.topic_attributes.get_aggregated_topic_attributes_repository"
    )
    @patch(
        "src.streaming.routers.topic_attributes.upsert_aggregated_topic_attributes_repository"
    )
    @patch(
        "src.streaming.routers.topic_attributes.update_aggregated_topic_attributes_dto_based_on_topic_attributes_event_schema"
    )
    async def test_transmit_topic_event_to_oltp_handler_existing_profile(
        self,
        mock_update_topic_attributes: MagicMock,
        mock_upsert_aggregated_topic_attributes: AsyncMock,
        mock_get_aggregated_topic_attributes: AsyncMock,
    ) -> None:
        # Arrange
        topic_event_uuid = uuid.uuid4()
        content_event_uuid = uuid.uuid4()
        user_id = "test_user_id"
        timestamp = utcnow()

        topic_event = TopicAttributesEventBrokerDTO(
            topic_attributes_event_uuid=topic_event_uuid,
            content_event_uuid=content_event_uuid,
            user_id=user_id,
            keywords=[KeywordTopicEventSchema(name="python", weight=0.8)],
            entities=[
                EntityTopicEventSchema(category="language", name="python", weight=0.8)
            ],
            sentiments=[SentimentTopicEventSchema(name="positive", weight=0.9)],
            timestamp=timestamp,
        )

        existing_topic_profile = {
            "user_id": user_id,
            "topic_attributes": {
                "keywords": [
                    {
                        "name": "fastapi",
                        "weight": 0.7,
                        "updated_at": "2023-01-01T00:00:00",
                    }
                ],
                "entities": [],
                "sentiments": [],
                "updated_at": "2023-01-01T00:00:00",
            },
        }

        mock_get_aggregated_topic_attributes.return_value = existing_topic_profile

        new_topic_attributes = AggregatedTopicAttributesDTO(
            user_id=user_id,
            keywords=[
                {"name": "python", "weight": 0.8, "updated_at": "2023-01-01T00:00:00"},
                {"name": "fastapi", "weight": 0.7, "updated_at": "2023-01-01T00:00:00"},
            ],
            entities=[
                {
                    "category": "language",
                    "name": "python",
                    "weight": 0.8,
                    "updated_at": "2023-01-01T00:00:00",
                }
            ],
            sentiments=[
                {"name": "positive", "weight": 0.9, "updated_at": "2023-01-01T00:00:00"}
            ],
            updated_at=utcnow(),
        )

        mock_update_topic_attributes.return_value = new_topic_attributes

        mock_database = MagicMock()
        state = State()
        state.mongo_database = mock_database

        # Act
        await transmit_topic_event_to_oltp_handler(
            topic_event,
            state=state,
        )

        # Assert
        mock_get_aggregated_topic_attributes.assert_called_once_with(
            user_id=user_id,
            database=mock_database,
        )

        # Verify update_topic_attributes was called with correct parameters
        mock_update_topic_attributes.assert_called_once()
        old_topic_attributes = mock_update_topic_attributes.call_args.args[0]
        # Just check that the object is of the correct type and has the expected user_id
        assert isinstance(old_topic_attributes, AggregatedTopicAttributesDTO)
        assert old_topic_attributes.user_id == user_id
        assert mock_update_topic_attributes.call_args.args[1] == topic_event

        # Verify upsert_topic_profile was called with correct parameters
        mock_upsert_aggregated_topic_attributes.assert_called_once()
        topic_profile_dto = mock_upsert_aggregated_topic_attributes.call_args.args[0]
        assert topic_profile_dto == new_topic_attributes.model_dump()
        assert (
            mock_upsert_aggregated_topic_attributes.call_args.kwargs["database"]
            == mock_database
        )

    @pytest.mark.asyncio
    @patch(
        "src.streaming.routers.topic_attributes.get_aggregated_topic_attributes_repository"
    )
    @patch(
        "src.streaming.routers.topic_attributes.upsert_aggregated_topic_attributes_repository"
    )
    @patch(
        "src.streaming.routers.topic_attributes.update_aggregated_topic_attributes_dto_based_on_topic_attributes_event_schema"
    )
    async def test_transmit_topic_event_to_oltp_handler_new_profile(
        self,
        mock_update_topic_attributes: MagicMock,
        mock_upsert_aggregated_topic_attributes: AsyncMock,
        mock_get_aggregated_topic_attributes: AsyncMock,
    ) -> None:
        # Arrange
        topic_event_uuid = uuid.uuid4()
        content_event_uuid = uuid.uuid4()
        user_id = "test_user_id"
        timestamp = utcnow()

        topic_event = TopicAttributesEventBrokerDTO(
            topic_attributes_event_uuid=topic_event_uuid,
            content_event_uuid=content_event_uuid,
            user_id=user_id,
            keywords=[KeywordTopicEventSchema(name="python", weight=0.8)],
            entities=[
                EntityTopicEventSchema(category="language", name="python", weight=0.8)
            ],
            sentiments=[SentimentTopicEventSchema(name="positive", weight=0.9)],
            timestamp=timestamp,
        )

        # No existing profile
        mock_get_aggregated_topic_attributes.return_value = None

        new_topic_attributes = AggregatedTopicAttributesDTO(
            user_id=user_id,
            keywords=[
                {"name": "python", "weight": 0.8, "updated_at": "2023-01-01T00:00:00"}
            ],
            entities=[
                {
                    "category": "language",
                    "name": "python",
                    "weight": 0.8,
                    "updated_at": "2023-01-01T00:00:00",
                }
            ],
            sentiments=[
                {"name": "positive", "weight": 0.9, "updated_at": "2023-01-01T00:00:00"}
            ],
            updated_at=utcnow(),
        )

        mock_update_topic_attributes.return_value = new_topic_attributes

        mock_database = MagicMock()
        state = State()
        state.mongo_database = mock_database

        # Act
        await transmit_topic_event_to_oltp_handler(
            topic_event,
            state=state,
        )

        # Assert
        mock_get_aggregated_topic_attributes.assert_called_once_with(
            user_id=user_id,
            database=mock_database,
        )

        # Verify update_topic_attributes was called with correct parameters
        mock_update_topic_attributes.assert_called_once()
        old_topic_attributes = mock_update_topic_attributes.call_args.args[0]
        assert isinstance(old_topic_attributes, AggregatedTopicAttributesDTO)

        # Compare the model dumps excluding the updated_at field which will be different
        old_dump = old_topic_attributes.model_dump()
        new_dump = AggregatedTopicAttributesDTO(user_id=user_id).model_dump()

        assert old_dump["keywords"] == new_dump["keywords"]
        assert old_dump["entities"] == new_dump["entities"]
        assert old_dump["sentiments"] == new_dump["sentiments"]
        assert mock_update_topic_attributes.call_args.args[1] == topic_event

        # Verify upsert_topic_profile was called with correct parameters
        mock_upsert_aggregated_topic_attributes.assert_called_once()
        topic_profile_dto = mock_upsert_aggregated_topic_attributes.call_args.args[0]
        assert topic_profile_dto == new_topic_attributes.model_dump()
        assert (
            mock_upsert_aggregated_topic_attributes.call_args.kwargs["database"]
            == mock_database
        )


class TestTransmitTopicEventToOlapHandler:
    @pytest.mark.asyncio
    @patch(
        "src.streaming.routers.topic_attributes.insert_topic_attributes_event_repository"
    )
    @patch("src.streaming.routers.topic_attributes.split_attributes_from_items")
    async def test_transmit_topic_event_to_olap_handler_success(
        self,
        mock_split_attributes: MagicMock,
        mock_insert_topic_attributes_event: AsyncMock,
    ) -> None:
        # Arrange
        topic_event_uuid = uuid.uuid4()
        content_event_uuid = uuid.uuid4()
        user_id = "test_user_id"
        timestamp = utcnow()

        topic_event = TopicAttributesEventBrokerDTO(
            topic_attributes_event_uuid=topic_event_uuid,
            content_event_uuid=content_event_uuid,
            user_id=user_id,
            keywords=[KeywordTopicEventSchema(name="python", weight=0.8)],
            entities=[
                EntityTopicEventSchema(category="language", name="python", weight=0.8)
            ],
            sentiments=[SentimentTopicEventSchema(name="positive", weight=0.9)],
            timestamp=timestamp,
        )

        # Mock split_attributes_from_items to return expected values
        mock_split_attributes.side_effect = [
            [["python"], [0.8]],  # keywords
            [["language"], ["python"], [0.8]],  # entities
            [["positive"], [0.9]],  # sentiments
        ]

        mock_get_clickhouse_connection = AsyncMock()
        state = State()
        state.get_clickhouse_connection = mock_get_clickhouse_connection

        # Act
        await transmit_topic_attributes_event_to_olap_handler(
            topic_event,
            state=state,
        )

        # Assert
        # Verify split_attributes_from_items was called for keywords, entities, and sentiments
        assert mock_split_attributes.call_count == 3

        # Verify insert_topic_event_repository was called with correct parameters
        mock_insert_topic_attributes_event.assert_called_once_with(
            keywords_names=["python"],
            keywords_weights=[0.8],
            entities_categories=["language"],
            entities_names=["python"],
            entities_weights=[0.8],
            sentiments_names=["positive"],
            sentiments_weights=[0.9],
            topic_attributes_event_uuid=topic_event_uuid,
            content_event_uuid=content_event_uuid,
            user_id=user_id,
            ts=timestamp,
            get_connection=mock_get_clickhouse_connection,
        )

    @pytest.mark.asyncio
    @patch(
        "src.streaming.routers.topic_attributes.insert_topic_attributes_event_repository"
    )
    @patch("src.streaming.routers.topic_attributes.split_attributes_from_items")
    async def test_transmit_topic_event_to_olap_handler_error(
        self,
        mock_split_attributes: MagicMock,
        mock_insert_topic_attributes_event: AsyncMock,
    ) -> None:
        # Arrange
        topic_event = TopicAttributesEventBrokerDTO(
            topic_attributes_event_uuid=uuid.uuid4(),
            content_event_uuid=uuid.uuid4(),
            user_id="test_user_id",
            keywords=[KeywordTopicEventSchema(name="python", weight=0.8)],
            entities=[
                EntityTopicEventSchema(category="language", name="python", weight=0.8)
            ],
            sentiments=[SentimentTopicEventSchema(name="positive", weight=0.9)],
            timestamp=utcnow(),
        )

        # Mock split_attributes_from_items to return expected values
        mock_split_attributes.side_effect = [
            [["python"], [0.8]],  # keywords
            [["language"], ["python"], [0.8]],  # entities
            [["positive"], [0.9]],  # sentiments
        ]

        mock_get_clickhouse_connection = AsyncMock()
        state = State()
        state.get_clickhouse_connection = mock_get_clickhouse_connection

        mock_insert_topic_attributes_event.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await transmit_topic_attributes_event_to_olap_handler(
                topic_event,
                state=state,
            )

        # Verify split_attributes_from_items was called for keywords, entities, and sentiments
        assert mock_split_attributes.call_count == 3

        # Verify insert_topic_event_repository was called
        mock_insert_topic_attributes_event.assert_called_once()
