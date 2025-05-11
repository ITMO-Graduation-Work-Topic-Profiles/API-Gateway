from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi_pagination import Params
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.repositories.users import (
    build_get_user_with_topic_profile_pipeline,
    build_get_users_with_topic_profiles_pipeline,
    get_user_repository,
    get_user_with_topic_profile_repository,
    get_users_with_topic_profiles_paginated_repository,
    insert_user_repository,
)


class TestBuildGetUsersWithTopicProfilesPipeline:
    def test_build_get_users_with_topic_profiles_pipeline_no_filters(self) -> None:
        # Act
        pipeline = build_get_users_with_topic_profiles_pipeline()

        # Assert
        assert isinstance(pipeline, list)
        assert len(pipeline) >= 3  # At least lookup, unwind, and sort stages

        # Verify lookup stage
        lookup_stage = next((stage for stage in pipeline if "$lookup" in stage), None)
        assert lookup_stage is not None
        assert lookup_stage["$lookup"]["from"] == "topic_profiles"
        assert lookup_stage["$lookup"]["localField"] == "user_id"
        assert lookup_stage["$lookup"]["foreignField"] == "user_id"

        # Verify unwind stage
        unwind_stage = next((stage for stage in pipeline if "$unwind" in stage), None)
        assert unwind_stage is not None
        assert unwind_stage["$unwind"]["path"] == "$topic_profile"
        assert unwind_stage["$unwind"]["preserveNullAndEmptyArrays"] is True

        # Verify sort stage
        sort_stage = next((stage for stage in pipeline if "$sort" in stage), None)
        assert sort_stage is not None

        # Verify no match stage when no filters
        match_stage = next((stage for stage in pipeline if "$match" in stage), None)
        assert match_stage is None

    def test_build_get_users_with_topic_profiles_pipeline_with_filters(self) -> None:
        # Arrange
        keywords = ["python", "fastapi"]
        entities = ["person"]
        sentiments = ["positive"]

        # Act
        pipeline = build_get_users_with_topic_profiles_pipeline(
            keywords=keywords,
            entities=entities,
            sentiments=sentiments,
        )

        # Assert
        assert isinstance(pipeline, list)

        # Verify match stage with filters
        match_stage = next((stage for stage in pipeline if "$match" in stage), None)
        assert match_stage is not None
        assert (
            match_stage["$match"]["topic_profile.topic_attributes.keywords.name"]["$in"]
            == keywords
        )
        assert (
            match_stage["$match"]["topic_profile.topic_attributes.entities.name"]["$in"]
            == entities
        )
        assert (
            match_stage["$match"]["topic_profile.topic_attributes.sentiments.name"][
                "$in"
            ]
            == sentiments
        )

        # Verify addFields stage with max weight calculations
        add_fields_stage = next(
            (stage for stage in pipeline if "$addFields" in stage), None
        )
        assert add_fields_stage is not None
        assert "maxKeywordWeight" in add_fields_stage["$addFields"]
        assert "maxEntityWeight" in add_fields_stage["$addFields"]
        assert "maxSentimentWeight" in add_fields_stage["$addFields"]


class TestGetUsersWithTopicProfilesPaginatedRepository:
    @pytest.mark.asyncio
    @patch("src.repositories.users.apaginate_aggregate")
    async def test_get_users_with_topic_profiles_paginated_repository(
        self, mock_apaginate_aggregate: AsyncMock
    ) -> None:
        # Arrange
        mock_database = MagicMock(spec=AsyncIOMotorDatabase)
        mock_database.__getitem__.return_value = MagicMock()
        mock_params = Params(page=1, size=10)
        mock_transformer = AsyncMock()

        expected_result = {"items": [], "total": 0, "page": 1, "size": 10}
        mock_apaginate_aggregate.return_value = expected_result

        # Act
        result = await get_users_with_topic_profiles_paginated_repository(
            database=mock_database,
            params=mock_params,
            transformer=mock_transformer,
            keywords=["python"],
            entities=["person"],
            sentiments=["positive"],
        )

        # Assert
        assert result == expected_result
        mock_apaginate_aggregate.assert_called_once()

        # Verify apaginate_aggregate was called with correct parameters
        call_args = mock_apaginate_aggregate.call_args
        assert call_args[0][0] == mock_database["users"]
        assert isinstance(call_args[0][1], list)  # pipeline
        assert call_args[0][2] == mock_params
        assert call_args[1]["transformer"] == mock_transformer


class TestBuildGetUserWithTopicProfilePipeline:
    def test_build_get_user_with_topic_profile_pipeline(self) -> None:
        # Arrange
        user_id = "test_user_id"

        # Act
        pipeline = build_get_user_with_topic_profile_pipeline(user_id=user_id)

        # Assert
        assert isinstance(pipeline, list)
        assert len(pipeline) == 3  # match, lookup, and unwind stages

        # Verify match stage
        match_stage = pipeline[0]
        assert "$match" in match_stage
        assert match_stage["$match"]["user_id"] == user_id

        # Verify lookup stage
        lookup_stage = pipeline[1]
        assert "$lookup" in lookup_stage
        assert lookup_stage["$lookup"]["from"] == "topic_profiles"
        assert lookup_stage["$lookup"]["localField"] == "user_id"
        assert lookup_stage["$lookup"]["foreignField"] == "user_id"

        # Verify unwind stage
        unwind_stage = pipeline[2]
        assert "$unwind" in unwind_stage
        assert unwind_stage["$unwind"]["path"] == "$topic_profile"
        assert unwind_stage["$unwind"]["preserveNullAndEmptyArrays"] is True


class TestGetUserWithTopicProfileRepository:
    @pytest.mark.asyncio
    async def test_get_user_with_topic_profile_repository_user_exists(self) -> None:
        # Arrange
        user_id = "test_user_id"
        expected_user = {
            "user_id": user_id,
            "username": "Test User",
            "topic_profile": {
                "topic_attributes": {
                    "keywords": [],
                    "entities": [],
                    "sentiments": [],
                }
            },
        }

        mock_aggregate = AsyncMock()
        mock_aggregate.to_list.return_value = [expected_user]

        mock_collection = MagicMock()
        mock_collection.aggregate.return_value = mock_aggregate

        mock_database = MagicMock(spec=AsyncIOMotorDatabase)
        mock_database.__getitem__.return_value = mock_collection

        # Act
        result = await get_user_with_topic_profile_repository(
            user_id=user_id,
            database=mock_database,
        )

        # Assert
        assert result == expected_user
        mock_database.__getitem__.assert_called_once_with("users")
        mock_collection.aggregate.assert_called_once()
        mock_aggregate.to_list.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_user_with_topic_profile_repository_user_not_exists(self) -> None:
        # Arrange
        user_id = "non_existent_user_id"

        mock_aggregate = AsyncMock()
        mock_aggregate.to_list.return_value = []

        mock_collection = MagicMock()
        mock_collection.aggregate.return_value = mock_aggregate

        mock_database = MagicMock(spec=AsyncIOMotorDatabase)
        mock_database.__getitem__.return_value = mock_collection

        # Act
        result = await get_user_with_topic_profile_repository(
            user_id=user_id,
            database=mock_database,
        )

        # Assert
        assert result is None
        mock_database.__getitem__.assert_called_once_with("users")
        mock_collection.aggregate.assert_called_once()
        mock_aggregate.to_list.assert_called_once_with(1)


class TestGetUserRepository:
    @pytest.mark.asyncio
    async def test_get_user_repository_user_exists(self) -> None:
        # Arrange
        user_id = "test_user_id"
        expected_user = {
            "user_id": user_id,
            "username": "Test User",
        }

        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value=expected_user)

        mock_database = MagicMock(spec=AsyncIOMotorDatabase)
        mock_database.__getitem__.return_value = mock_collection

        # Act
        result = await get_user_repository(
            user_id=user_id,
            database=mock_database,
        )

        # Assert
        assert result == expected_user
        mock_database.__getitem__.assert_called_once_with("users")
        mock_collection.find_one.assert_called_once_with({"user_id": user_id})

    @pytest.mark.asyncio
    async def test_get_user_repository_user_not_exists(self) -> None:
        # Arrange
        user_id = "non_existent_user_id"

        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value=None)

        mock_database = MagicMock(spec=AsyncIOMotorDatabase)
        mock_database.__getitem__.return_value = mock_collection

        # Act
        result = await get_user_repository(
            user_id=user_id,
            database=mock_database,
        )

        # Assert
        assert result is None
        mock_database.__getitem__.assert_called_once_with("users")
        mock_collection.find_one.assert_called_once_with({"user_id": user_id})


class TestInsertUserRepository:
    @pytest.mark.asyncio
    async def test_insert_user_repository_success(self) -> None:
        # Arrange
        user_data = {
            "user_id": "test_user_id",
            "username": "Test User",
        }

        mock_collection = MagicMock()
        mock_collection.insert_one = AsyncMock()

        mock_database = MagicMock(spec=AsyncIOMotorDatabase)
        mock_database.__getitem__.return_value = mock_collection

        # Act
        await insert_user_repository(
            data=user_data,
            database=mock_database,
        )

        # Assert
        mock_database.__getitem__.assert_called_once_with("users")
        mock_collection.insert_one.assert_called_once_with(user_data)

    @pytest.mark.asyncio
    async def test_insert_user_repository_error(self) -> None:
        # Arrange
        user_data = {
            "user_id": "test_user_id",
            "username": "Test User",
        }

        mock_collection = MagicMock()
        mock_collection.insert_one = AsyncMock(side_effect=Exception("Database error"))

        mock_database = MagicMock(spec=AsyncIOMotorDatabase)
        mock_database.__getitem__.return_value = mock_collection

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await insert_user_repository(
                data=user_data,
                database=mock_database,
            )

        mock_database.__getitem__.assert_called_once_with("users")
        mock_collection.insert_one.assert_called_once_with(user_data)
