import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from src.dtos.events import TopicEventBrokerDTO
from src.schemas import (
    EntityTopicEventSchema,
    EntityTopicProfileSchema,
    KeywordTopicEventSchema,
    KeywordTopicProfileSchema,
    SentimentTopicEventSchema,
    SentimentTopicProfileSchema,
    TopicProfileSchema,
)
from src.utils.topic_profiles import (
    build_key_from_item_fields,
    merge_entities,
    merge_entities_schemas,
    merge_keywords,
    merge_keywords_schemas,
    merge_sentiment,
    merge_sentiment_schemas,
    merge_weighted_item_lists,
    update_topic_profile_schema_based_on_topic_event_schema,
)


@pytest.fixture
def mock_time() -> datetime:
    return datetime(2023, 1, 1, tzinfo=timezone.utc)


class TestBuildKeyFromItemFields:
    def test_single_field(self) -> None:
        item = {"id": 1, "name": "test", "value": 10}
        key_fields = ["id"]

        result = build_key_from_item_fields(key_fields, item)

        assert result == (1,)

    def test_multiple_fields(self) -> None:
        item = {"id": 1, "name": "test", "value": 10}
        key_fields = ["id", "name"]

        result = build_key_from_item_fields(key_fields, item)

        assert result == (1, "test")

    def test_all_fields(self) -> None:
        item = {"id": 1, "name": "test", "value": 10}
        key_fields = ["id", "name", "value"]

        result = build_key_from_item_fields(key_fields, item)

        assert result == (1, "test", 10)

    def test_missing_field(self) -> None:
        item = {"id": 1, "name": "test"}
        key_fields = ["id", "missing_field"]

        with pytest.raises(KeyError):
            build_key_from_item_fields(key_fields, item)


class TestMergeWeightedItemLists:
    @patch("src.utils.topic_profiles.utcnow")
    def test_empty_lists(self, mock_utcnow: MagicMock, mock_time: datetime) -> None:
        mock_utcnow.return_value = mock_time

        result = merge_weighted_item_lists(
            existing_item_list=[],
            incoming_item_list=[],
            key_fields=["id"],
            weight_field="weight",
            timestamp_field="timestamp",
            limit=10,
            alpha=0.8,
        )

        assert result == []

    @patch("src.utils.topic_profiles.utcnow")
    def test_new_items_only(self, mock_utcnow: MagicMock, mock_time: datetime) -> None:
        mock_utcnow.return_value = mock_time

        incoming_items = [
            {"id": 1, "name": "item1", "weight": 0.8},
            {"id": 2, "name": "item2", "weight": 0.5},
        ]

        result = merge_weighted_item_lists(
            existing_item_list=[],
            incoming_item_list=incoming_items,
            key_fields=["id"],
            weight_field="weight",
            timestamp_field="timestamp",
            limit=10,
            alpha=0.8,
        )

        expected = [
            {"id": 1, "name": "item1", "weight": 0.8, "timestamp": mock_time},
            {"id": 2, "name": "item2", "weight": 0.5, "timestamp": mock_time},
        ]

        assert result == expected

    @patch("src.utils.topic_profiles.utcnow")
    def test_existing_items_only(self, mock_utcnow: MagicMock) -> None:
        mock_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
        mock_utcnow.return_value = mock_time

        existing_items = [
            {
                "id": 1,
                "name": "item1",
                "weight": 0.8,
                "timestamp": datetime(2022, 1, 1, tzinfo=timezone.utc),
            },
            {
                "id": 2,
                "name": "item2",
                "weight": 0.5,
                "timestamp": datetime(2022, 1, 1, tzinfo=timezone.utc),
            },
        ]

        result = merge_weighted_item_lists(
            existing_item_list=existing_items,
            incoming_item_list=[],
            key_fields=["id"],
            weight_field="weight",
            timestamp_field="timestamp",
            limit=10,
            alpha=0.8,
        )

        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[0]["name"] == "item1"
        assert result[0]["weight"] == 0.8
        assert result[0]["timestamp"] == datetime(2022, 1, 1, tzinfo=timezone.utc)

        assert result[1]["id"] == 2
        assert result[1]["name"] == "item2"
        assert result[1]["weight"] == 0.5
        assert result[1]["timestamp"] == datetime(2022, 1, 1, tzinfo=timezone.utc)

    @patch("src.utils.topic_profiles.utcnow")
    def test_merge_with_existing_items(
        self, mock_utcnow: MagicMock, mock_time: datetime
    ) -> None:
        mock_utcnow.return_value = mock_time

        existing_items = [
            {
                "id": 1,
                "name": "item1",
                "weight": 0.8,
                "timestamp": datetime(2022, 1, 1, tzinfo=timezone.utc),
            },
            {
                "id": 2,
                "name": "item2",
                "weight": 0.5,
                "timestamp": datetime(2022, 1, 1, tzinfo=timezone.utc),
            },
        ]

        incoming_items = [
            {"id": 1, "name": "item1_updated", "weight": 0.9},
            {"id": 3, "name": "item3", "weight": 0.7},
        ]

        result = merge_weighted_item_lists(
            existing_item_list=existing_items,
            incoming_item_list=incoming_items,
            key_fields=["id"],
            weight_field="weight",
            timestamp_field="timestamp",
            limit=10,
            alpha=0.8,
        )

        assert len(result) == 3

        assert result[0]["id"] == 1
        assert result[0]["name"] == "item1"
        assert result[0]["weight"] == 0.82
        assert result[0]["timestamp"] == mock_time

        assert result[1]["id"] == 3
        assert result[1]["name"] == "item3"
        assert result[1]["weight"] == 0.7
        assert result[1]["timestamp"] == mock_time

        assert result[2]["id"] == 2
        assert result[2]["name"] == "item2"
        assert result[2]["weight"] == 0.5
        assert result[2]["timestamp"] == datetime(2022, 1, 1, tzinfo=timezone.utc)

    @patch("src.utils.topic_profiles.utcnow")
    def test_merge_with_additional_fields(
        self, mock_utcnow: MagicMock, mock_time: datetime
    ) -> None:
        mock_utcnow.return_value = mock_time

        existing_items = [
            {
                "id": 1,
                "name": "item1",
                "weight": 0.8,
                "timestamp": datetime(2022, 1, 1, tzinfo=timezone.utc),
            },
        ]

        incoming_items = [
            {"id": 1, "name": "item1", "weight": 0.9, "extra_field": "extra_value"},
        ]

        result = merge_weighted_item_lists(
            existing_item_list=existing_items,
            incoming_item_list=incoming_items,
            key_fields=["id"],
            weight_field="weight",
            timestamp_field="timestamp",
            limit=10,
            alpha=0.8,
        )

        assert len(result) == 1
        assert result[0]["id"] == 1
        assert result[0]["name"] == "item1"
        assert result[0]["weight"] == 0.82
        assert result[0]["timestamp"] == mock_time
        assert result[0]["extra_field"] == "extra_value"

    @patch("src.utils.topic_profiles.utcnow")
    def test_limit_applied(self, mock_utcnow: MagicMock, mock_time: datetime) -> None:
        mock_utcnow.return_value = mock_time

        incoming_items = [
            {"id": 1, "weight": 0.5},
            {"id": 2, "weight": 0.8},
            {"id": 3, "weight": 0.3},
        ]

        result = merge_weighted_item_lists(
            existing_item_list=[],
            incoming_item_list=incoming_items,
            key_fields=["id"],
            weight_field="weight",
            timestamp_field="timestamp",
            limit=2,
            alpha=0.8,
        )

        assert len(result) == 2
        assert result[0]["id"] == 2
        assert result[1]["id"] == 1

    @patch("src.utils.topic_profiles.utcnow")
    def test_composite_key(self, mock_utcnow: MagicMock, mock_time: datetime) -> None:
        mock_utcnow.return_value = mock_time

        existing_items = [
            {
                "type": "A",
                "id": 1,
                "weight": 0.8,
                "timestamp": datetime(2022, 1, 1, tzinfo=timezone.utc),
            },
            {
                "type": "B",
                "id": 1,
                "weight": 0.5,
                "timestamp": datetime(2022, 1, 1, tzinfo=timezone.utc),
            },
        ]

        incoming_items = [
            {"type": "A", "id": 1, "weight": 0.9},
            {"type": "C", "id": 1, "weight": 0.7},
        ]

        result = merge_weighted_item_lists(
            existing_item_list=existing_items,
            incoming_item_list=incoming_items,
            key_fields=["type", "id"],
            weight_field="weight",
            timestamp_field="timestamp",
            limit=10,
            alpha=0.8,
        )

        assert len(result) == 3

        assert result[0]["type"] == "A"
        assert result[0]["id"] == 1
        assert result[0]["weight"] == 0.82
        assert result[0]["timestamp"] == mock_time

        assert result[1]["type"] == "C"
        assert result[1]["id"] == 1
        assert result[1]["weight"] == 0.7
        assert result[1]["timestamp"] == mock_time

        assert result[2]["type"] == "B"
        assert result[2]["id"] == 1
        assert result[2]["weight"] == 0.5
        assert result[2]["timestamp"] == datetime(2022, 1, 1, tzinfo=timezone.utc)


class TestMergeKeywords:
    @patch("src.utils.topic_profiles.merge_weighted_item_lists")
    def test_merge_keywords_calls_merge_weighted_item_lists_with_correct_params(
        self, mock_merge_weighted_item_lists: MagicMock
    ) -> None:
        existing_keywords = [{"name": "keyword1", "weight": 0.8}]
        incoming_keywords = [{"name": "keyword2", "weight": 0.9}]
        mock_result = [{"name": "result", "weight": 0.85}]
        mock_merge_weighted_item_lists.return_value = mock_result

        result = merge_keywords(existing_keywords, incoming_keywords)

        mock_merge_weighted_item_lists.assert_called_once_with(
            existing_keywords,
            incoming_keywords,
            key_fields=("name",),
            weight_field="weight",
            timestamp_field="updated_at",
            limit=50,
            alpha=0.8,
        )
        assert result == mock_result

    @patch("src.utils.topic_profiles.utcnow")
    def test_merge_keywords_integration(
        self, mock_utcnow: MagicMock, mock_time: datetime
    ) -> None:
        mock_utcnow.return_value = mock_time

        existing_keywords = [
            {
                "name": "keyword1",
                "weight": 0.8,
                "updated_at": datetime(2022, 1, 1, tzinfo=timezone.utc),
            },
            {
                "name": "keyword2",
                "weight": 0.5,
                "updated_at": datetime(2022, 1, 1, tzinfo=timezone.utc),
            },
        ]

        incoming_keywords = [
            {"name": "keyword1", "weight": 0.9},
            {"name": "keyword3", "weight": 0.7},
        ]

        result = merge_keywords(existing_keywords, incoming_keywords)

        assert len(result) == 3
        assert result[0]["name"] == "keyword1"
        assert result[0]["weight"] == 0.82
        assert result[0]["updated_at"] == mock_time

        assert result[1]["name"] == "keyword3"
        assert result[1]["weight"] == 0.7
        assert result[1]["updated_at"] == mock_time

        assert result[2]["name"] == "keyword2"
        assert result[2]["weight"] == 0.5
        assert result[2]["updated_at"] == datetime(2022, 1, 1, tzinfo=timezone.utc)

    def test_merge_keywords_empty_lists(self) -> None:
        result = merge_keywords([], [])
        assert result == []


class TestMergeEntities:
    @patch("src.utils.topic_profiles.merge_weighted_item_lists")
    def test_merge_entities_calls_merge_weighted_item_lists_with_correct_params(
        self, mock_merge_weighted_item_lists: MagicMock
    ) -> None:
        existing_entities = [{"category": "person", "name": "entity1", "weight": 0.8}]
        incoming_entities = [{"category": "location", "name": "entity2", "weight": 0.9}]
        mock_result = [{"category": "result", "name": "result", "weight": 0.85}]
        mock_merge_weighted_item_lists.return_value = mock_result

        result = merge_entities(existing_entities, incoming_entities)

        mock_merge_weighted_item_lists.assert_called_once_with(
            existing_entities,
            incoming_entities,
            key_fields=("category", "name"),
            weight_field="weight",
            timestamp_field="updated_at",
            limit=50,
            alpha=0.8,
        )
        assert result == mock_result

    @patch("src.utils.topic_profiles.utcnow")
    def test_merge_entities_integration(
        self, mock_utcnow: MagicMock, mock_time: datetime
    ) -> None:
        mock_utcnow.return_value = mock_time

        existing_entities = [
            {
                "category": "person",
                "name": "entity1",
                "weight": 0.8,
                "updated_at": datetime(2022, 1, 1, tzinfo=timezone.utc),
            },
            {
                "category": "location",
                "name": "entity2",
                "weight": 0.5,
                "updated_at": datetime(2022, 1, 1, tzinfo=timezone.utc),
            },
        ]

        incoming_entities = [
            {"category": "person", "name": "entity1", "weight": 0.9},
            {"category": "organization", "name": "entity3", "weight": 0.7},
        ]

        result = merge_entities(existing_entities, incoming_entities)

        assert len(result) == 3
        assert result[0]["category"] == "person"
        assert result[0]["name"] == "entity1"
        assert result[0]["weight"] == 0.82
        assert result[0]["updated_at"] == mock_time

        assert result[1]["category"] == "organization"
        assert result[1]["name"] == "entity3"
        assert result[1]["weight"] == 0.7
        assert result[1]["updated_at"] == mock_time

        assert result[2]["category"] == "location"
        assert result[2]["name"] == "entity2"
        assert result[2]["weight"] == 0.5
        assert result[2]["updated_at"] == datetime(2022, 1, 1, tzinfo=timezone.utc)

    def test_merge_entities_empty_lists(self) -> None:
        result = merge_entities([], [])
        assert result == []


class TestMergeSentiment:
    @patch("src.utils.topic_profiles.merge_weighted_item_lists")
    def test_merge_sentiment_calls_merge_weighted_item_lists_with_correct_params(
        self, mock_merge_weighted_item_lists: MagicMock
    ) -> None:
        existing_sentiment = [{"name": "positive", "weight": 0.8}]
        incoming_sentiment = [{"name": "negative", "weight": 0.9}]
        mock_result = [{"name": "result", "weight": 0.85}]
        mock_merge_weighted_item_lists.return_value = mock_result

        result = merge_sentiment(existing_sentiment, incoming_sentiment)

        mock_merge_weighted_item_lists.assert_called_once_with(
            existing_sentiment,
            incoming_sentiment,
            key_fields=("name",),
            weight_field="weight",
            timestamp_field="updated_at",
            limit=50,
            alpha=0.8,
        )
        assert result == mock_result

    @patch("src.utils.topic_profiles.utcnow")
    def test_merge_sentiment_integration(
        self, mock_utcnow: MagicMock, mock_time: datetime
    ) -> None:
        mock_utcnow.return_value = mock_time

        existing_sentiment = [
            {
                "name": "positive",
                "weight": 0.8,
                "updated_at": datetime(2022, 1, 1, tzinfo=timezone.utc),
            },
            {
                "name": "negative",
                "weight": 0.5,
                "updated_at": datetime(2022, 1, 1, tzinfo=timezone.utc),
            },
        ]

        incoming_sentiment = [
            {"name": "positive", "weight": 0.9},
            {"name": "neutral", "weight": 0.7},
        ]

        result = merge_sentiment(existing_sentiment, incoming_sentiment)

        assert len(result) == 3
        assert result[0]["name"] == "positive"
        assert result[0]["weight"] == 0.82
        assert result[0]["updated_at"] == mock_time

        assert result[1]["name"] == "neutral"
        assert result[1]["weight"] == 0.7
        assert result[1]["updated_at"] == mock_time

        assert result[2]["name"] == "negative"
        assert result[2]["weight"] == 0.5
        assert result[2]["updated_at"] == datetime(2022, 1, 1, tzinfo=timezone.utc)

    def test_merge_sentiment_empty_lists(self) -> None:
        result = merge_sentiment([], [])
        assert result == []


class TestMergeKeywordsSchemas:
    @patch("src.utils.topic_profiles.merge_keywords")
    def test_merge_keywords_schemas_calls_merge_keywords_with_correct_params(
        self, mock_merge_keywords: MagicMock
    ) -> None:
        existing_keywords = [
            KeywordTopicProfileSchema(name="keyword1", weight=0.8),
            KeywordTopicProfileSchema(name="keyword2", weight=0.5),
        ]
        incoming_keywords = [
            KeywordTopicEventSchema(name="keyword1", weight=0.9),
            KeywordTopicEventSchema(name="keyword3", weight=0.7),
        ]
        mock_result = [
            {
                "name": "keyword1",
                "weight": 0.82,
                "updated_at": datetime(2023, 1, 1, tzinfo=timezone.utc),
            },
            {
                "name": "keyword3",
                "weight": 0.7,
                "updated_at": datetime(2023, 1, 1, tzinfo=timezone.utc),
            },
        ]
        mock_merge_keywords.return_value = mock_result

        result = merge_keywords_schemas(existing_keywords, incoming_keywords)

        mock_merge_keywords.assert_called_once_with(
            [kw.model_dump() for kw in existing_keywords],
            [kw.model_dump() for kw in incoming_keywords],
        )
        assert len(result) == 2
        assert isinstance(result[0], KeywordTopicProfileSchema)
        assert result[0].name == "keyword1"
        assert result[0].weight == 0.82
        assert result[0].updated_at == datetime(2023, 1, 1, tzinfo=timezone.utc)
        assert isinstance(result[1], KeywordTopicProfileSchema)
        assert result[1].name == "keyword3"
        assert result[1].weight == 0.7
        assert result[1].updated_at == datetime(2023, 1, 1, tzinfo=timezone.utc)

    def test_merge_keywords_schemas_empty_lists(self) -> None:
        result = merge_keywords_schemas([], [])
        assert result == []

    @patch("src.utils.topic_profiles.utcnow")
    def test_merge_keywords_schemas_integration(
        self, mock_utcnow: MagicMock, mock_time: datetime
    ) -> None:
        mock_utcnow.return_value = mock_time

        existing_keywords = [
            KeywordTopicProfileSchema(
                name="keyword1",
                weight=0.8,
                updated_at=datetime(2022, 1, 1, tzinfo=timezone.utc),
            ),
            KeywordTopicProfileSchema(
                name="keyword2",
                weight=0.5,
                updated_at=datetime(2022, 1, 1, tzinfo=timezone.utc),
            ),
        ]

        incoming_keywords = [
            KeywordTopicEventSchema(name="keyword1", weight=0.9),
            KeywordTopicEventSchema(name="keyword3", weight=0.7),
        ]

        result = merge_keywords_schemas(existing_keywords, incoming_keywords)

        assert len(result) == 3
        assert result[0].name == "keyword1"
        assert result[0].weight == 0.82
        assert result[0].updated_at == mock_time

        assert result[1].name == "keyword3"
        assert result[1].weight == 0.7
        assert result[1].updated_at == mock_time

        assert result[2].name == "keyword2"
        assert result[2].weight == 0.5
        assert result[2].updated_at == datetime(2022, 1, 1, tzinfo=timezone.utc)


class TestMergeEntitiesSchemas:
    @patch("src.utils.topic_profiles.merge_entities")
    def test_merge_entities_schemas_calls_merge_entities_with_correct_params(
        self, mock_merge_entities: MagicMock
    ) -> None:
        existing_entities = [
            EntityTopicProfileSchema(category="person", name="entity1", weight=0.8),
            EntityTopicProfileSchema(category="location", name="entity2", weight=0.5),
        ]
        incoming_entities = [
            EntityTopicEventSchema(category="person", name="entity1", weight=0.9),
            EntityTopicEventSchema(category="organization", name="entity3", weight=0.7),
        ]
        mock_result = [
            {
                "category": "person",
                "name": "entity1",
                "weight": 0.82,
                "updated_at": datetime(2023, 1, 1, tzinfo=timezone.utc),
            },
            {
                "category": "organization",
                "name": "entity3",
                "weight": 0.7,
                "updated_at": datetime(2023, 1, 1, tzinfo=timezone.utc),
            },
        ]
        mock_merge_entities.return_value = mock_result

        result = merge_entities_schemas(existing_entities, incoming_entities)

        mock_merge_entities.assert_called_once_with(
            [et.model_dump() for et in existing_entities],
            [et.model_dump() for et in incoming_entities],
        )
        assert len(result) == 2
        assert isinstance(result[0], EntityTopicProfileSchema)
        assert result[0].category == "person"
        assert result[0].name == "entity1"
        assert result[0].weight == 0.82
        assert result[0].updated_at == datetime(2023, 1, 1, tzinfo=timezone.utc)
        assert isinstance(result[1], EntityTopicProfileSchema)
        assert result[1].category == "organization"
        assert result[1].name == "entity3"
        assert result[1].weight == 0.7
        assert result[1].updated_at == datetime(2023, 1, 1, tzinfo=timezone.utc)

    def test_merge_entities_schemas_empty_lists(self) -> None:
        result = merge_entities_schemas([], [])
        assert result == []

    @patch("src.utils.topic_profiles.utcnow")
    def test_merge_entities_schemas_integration(
        self, mock_utcnow: MagicMock, mock_time: datetime
    ) -> None:
        mock_utcnow.return_value = mock_time

        existing_entities = [
            EntityTopicProfileSchema(
                category="person",
                name="entity1",
                weight=0.8,
                updated_at=datetime(2022, 1, 1, tzinfo=timezone.utc),
            ),
            EntityTopicProfileSchema(
                category="location",
                name="entity2",
                weight=0.5,
                updated_at=datetime(2022, 1, 1, tzinfo=timezone.utc),
            ),
        ]

        incoming_entities = [
            EntityTopicEventSchema(category="person", name="entity1", weight=0.9),
            EntityTopicEventSchema(category="organization", name="entity3", weight=0.7),
        ]

        result = merge_entities_schemas(existing_entities, incoming_entities)

        assert len(result) == 3
        assert result[0].category == "person"
        assert result[0].name == "entity1"
        assert result[0].weight == 0.82
        assert result[0].updated_at == mock_time

        assert result[1].category == "organization"
        assert result[1].name == "entity3"
        assert result[1].weight == 0.7
        assert result[1].updated_at == mock_time

        assert result[2].category == "location"
        assert result[2].name == "entity2"
        assert result[2].weight == 0.5
        assert result[2].updated_at == datetime(2022, 1, 1, tzinfo=timezone.utc)


class TestMergeSentimentSchemas:
    @patch("src.utils.topic_profiles.merge_sentiment")
    def test_merge_sentiment_schemas_calls_merge_sentiment_with_correct_params(
        self, mock_merge_sentiment: MagicMock
    ) -> None:
        existing_sentiment = [
            SentimentTopicProfileSchema(name="positive", weight=0.8),
            SentimentTopicProfileSchema(name="negative", weight=0.5),
        ]
        incoming_sentiment = [
            SentimentTopicEventSchema(name="positive", weight=0.9),
            SentimentTopicEventSchema(name="neutral", weight=0.7),
        ]
        mock_result = [
            {
                "name": "positive",
                "weight": 0.82,
                "updated_at": datetime(2023, 1, 1, tzinfo=timezone.utc),
            },
            {
                "name": "neutral",
                "weight": 0.7,
                "updated_at": datetime(2023, 1, 1, tzinfo=timezone.utc),
            },
        ]
        mock_merge_sentiment.return_value = mock_result

        result = merge_sentiment_schemas(existing_sentiment, incoming_sentiment)

        mock_merge_sentiment.assert_called_once_with(
            [st.model_dump() for st in existing_sentiment],
            [st.model_dump() for st in incoming_sentiment],
        )
        assert len(result) == 2
        assert isinstance(result[0], SentimentTopicProfileSchema)
        assert result[0].name == "positive"
        assert result[0].weight == 0.82
        assert result[0].updated_at == datetime(2023, 1, 1, tzinfo=timezone.utc)
        assert isinstance(result[1], SentimentTopicProfileSchema)
        assert result[1].name == "neutral"
        assert result[1].weight == 0.7
        assert result[1].updated_at == datetime(2023, 1, 1, tzinfo=timezone.utc)

    def test_merge_sentiment_schemas_empty_lists(self) -> None:
        result = merge_sentiment_schemas([], [])
        assert result == []

    @patch("src.utils.topic_profiles.utcnow")
    def test_merge_sentiment_schemas_integration(
        self, mock_utcnow: MagicMock, mock_time: datetime
    ) -> None:
        mock_utcnow.return_value = mock_time

        existing_sentiment = [
            SentimentTopicProfileSchema(
                name="positive",
                weight=0.8,
                updated_at=datetime(2022, 1, 1, tzinfo=timezone.utc),
            ),
            SentimentTopicProfileSchema(
                name="negative",
                weight=0.5,
                updated_at=datetime(2022, 1, 1, tzinfo=timezone.utc),
            ),
        ]

        incoming_sentiment = [
            SentimentTopicEventSchema(name="positive", weight=0.9),
            SentimentTopicEventSchema(name="neutral", weight=0.7),
        ]

        result = merge_sentiment_schemas(existing_sentiment, incoming_sentiment)

        assert len(result) == 3
        assert result[0].name == "positive"
        assert result[0].weight == 0.82
        assert result[0].updated_at == mock_time

        assert result[1].name == "neutral"
        assert result[1].weight == 0.7
        assert result[1].updated_at == mock_time

        assert result[2].name == "negative"
        assert result[2].weight == 0.5
        assert result[2].updated_at == datetime(2022, 1, 1, tzinfo=timezone.utc)


class TestUpdateTopicProfileSchemaBasedOnTopicEventSchema:
    @patch("src.utils.topic_profiles.utcnow")
    def test_update_topic_profile_schema_based_on_topic_event_schema(
        self, mock_utcnow: MagicMock, mock_time: datetime
    ) -> None:
        mock_utcnow.return_value = mock_time

        existing_topic_profile = TopicProfileSchema(
            keywords=[
                KeywordTopicProfileSchema(
                    name="keyword1",
                    weight=0.8,
                    updated_at=datetime(2022, 1, 1, tzinfo=timezone.utc),
                ),
                KeywordTopicProfileSchema(
                    name="keyword2",
                    weight=0.5,
                    updated_at=datetime(2022, 1, 1, tzinfo=timezone.utc),
                ),
            ],
            entities=[
                EntityTopicProfileSchema(
                    category="person",
                    name="entity1",
                    weight=0.8,
                    updated_at=datetime(2022, 1, 1, tzinfo=timezone.utc),
                ),
                EntityTopicProfileSchema(
                    category="location",
                    name="entity2",
                    weight=0.5,
                    updated_at=datetime(2022, 1, 1, tzinfo=timezone.utc),
                ),
            ],
            sentiments=[
                SentimentTopicProfileSchema(
                    name="positive",
                    weight=0.8,
                    updated_at=datetime(2022, 1, 1, tzinfo=timezone.utc),
                ),
                SentimentTopicProfileSchema(
                    name="negative",
                    weight=0.5,
                    updated_at=datetime(2022, 1, 1, tzinfo=timezone.utc),
                ),
            ],
            updated_at=datetime(2022, 1, 1, tzinfo=timezone.utc),
        )

        incoming_topic_event = TopicEventBrokerDTO(
            topic_event_uuid=uuid.uuid4(),
            content_event_uuid=uuid.uuid4(),
            user_id="user123",
            keywords=[
                KeywordTopicEventSchema(name="keyword1", weight=0.9),
                KeywordTopicEventSchema(name="keyword3", weight=0.7),
            ],
            entities=[
                EntityTopicEventSchema(category="person", name="entity1", weight=0.9),
                EntityTopicEventSchema(
                    category="organization", name="entity3", weight=0.7
                ),
            ],
            sentiment=SentimentTopicEventSchema(name="positive", weight=0.9),
            timestamp=datetime(2023, 1, 1, tzinfo=timezone.utc),
        )

        # Call the function
        result = update_topic_profile_schema_based_on_topic_event_schema(
            existing_topic_profile, incoming_topic_event
        )

        # Verify the result
        assert isinstance(result, TopicProfileSchema)
        assert result.updated_at == mock_time

        # Verify keywords
        assert len(result.keywords) == 3
        assert result.keywords[0].name == "keyword1"
        assert result.keywords[0].weight == 0.82
        assert result.keywords[0].updated_at == mock_time
        assert result.keywords[1].name == "keyword3"
        assert result.keywords[1].weight == 0.7
        assert result.keywords[1].updated_at == mock_time
        assert result.keywords[2].name == "keyword2"
        assert result.keywords[2].weight == 0.5
        assert result.keywords[2].updated_at == datetime(
            2022, 1, 1, tzinfo=timezone.utc
        )

        # Verify entities
        assert len(result.entities) == 3
        assert result.entities[0].category == "person"
        assert result.entities[0].name == "entity1"
        assert result.entities[0].weight == 0.82
        assert result.entities[0].updated_at == mock_time
        assert result.entities[1].category == "organization"
        assert result.entities[1].name == "entity3"
        assert result.entities[1].weight == 0.7
        assert result.entities[1].updated_at == mock_time
        assert result.entities[2].category == "location"
        assert result.entities[2].name == "entity2"
        assert result.entities[2].weight == 0.5
        assert result.entities[2].updated_at == datetime(
            2022, 1, 1, tzinfo=timezone.utc
        )

        # Verify sentiment
        assert len(result.sentiments) == 2
        assert result.sentiments[0].name == "positive"
        assert result.sentiments[0].weight == 0.82
        assert result.sentiments[0].updated_at == mock_time
        assert result.sentiments[1].name == "negative"
        assert result.sentiments[1].weight == 0.5
        assert result.sentiments[1].updated_at == datetime(
            2022, 1, 1, tzinfo=timezone.utc
        )

    @patch("src.utils.topic_profiles.utcnow")
    def test_update_topic_profile_schema_based_on_topic_event_schema_empty_profile(
        self, mock_utcnow: MagicMock, mock_time: datetime
    ) -> None:
        mock_utcnow.return_value = mock_time

        # Create empty existing topic profile
        existing_topic_profile = TopicProfileSchema()

        # Create incoming topic event
        incoming_topic_event = TopicEventBrokerDTO(
            topic_event_uuid=uuid.uuid4(),
            content_event_uuid=uuid.uuid4(),
            user_id="user123",
            keywords=[
                KeywordTopicEventSchema(name="keyword1", weight=0.9),
                KeywordTopicEventSchema(name="keyword2", weight=0.7),
            ],
            entities=[
                EntityTopicEventSchema(category="person", name="entity1", weight=0.9),
                EntityTopicEventSchema(
                    category="organization", name="entity2", weight=0.7
                ),
            ],
            sentiment=SentimentTopicEventSchema(name="positive", weight=0.9),
            timestamp=datetime(2023, 1, 1, tzinfo=timezone.utc),
        )

        # Call the function
        result = update_topic_profile_schema_based_on_topic_event_schema(
            existing_topic_profile, incoming_topic_event
        )

        # Verify the result
        assert isinstance(result, TopicProfileSchema)
        assert result.updated_at == mock_time

        # Verify keywords
        assert len(result.keywords) == 2
        assert result.keywords[0].name == "keyword1"
        assert result.keywords[0].weight == 0.9
        assert result.keywords[0].updated_at == mock_time
        assert result.keywords[1].name == "keyword2"
        assert result.keywords[1].weight == 0.7
        assert result.keywords[1].updated_at == mock_time

        # Verify entities
        assert len(result.entities) == 2
        assert result.entities[0].category == "person"
        assert result.entities[0].name == "entity1"
        assert result.entities[0].weight == 0.9
        assert result.entities[0].updated_at == mock_time
        assert result.entities[1].category == "organization"
        assert result.entities[1].name == "entity2"
        assert result.entities[1].weight == 0.7
        assert result.entities[1].updated_at == mock_time

        # Verify sentiment
        assert len(result.sentiments) == 1
        assert result.sentiments[0].name == "positive"
        assert result.sentiments[0].weight == 0.9
        assert result.sentiments[0].updated_at == mock_time
