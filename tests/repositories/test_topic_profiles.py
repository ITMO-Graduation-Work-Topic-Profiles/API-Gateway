from unittest.mock import AsyncMock, MagicMock

import pytest
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.repositories.aggregated_topic_attributes import (
    get_aggregated_topic_attributes_repository,
    upsert_aggregated_topic_attributes_repository,
)


class TestGetTopicProfileRepository:
    @pytest.mark.asyncio
    async def test_get_topic_profile_repository_profile_exists(self) -> None:
        # Arrange
        user_id = "test_user_id"
        expected_profile = {
            "user_id": user_id,
            "topic_attributes": {
                "keywords": [
                    {
                        "name": "python",
                        "weight": 0.8,
                        "updated_at": "2023-01-01T00:00:00",
                    }
                ],
                "entities": [
                    {
                        "category": "language",
                        "name": "python",
                        "weight": 0.8,
                        "updated_at": "2023-01-01T00:00:00",
                    }
                ],
                "sentiments": [
                    {
                        "name": "positive",
                        "weight": 0.9,
                        "updated_at": "2023-01-01T00:00:00",
                    }
                ],
                "updated_at": "2023-01-01T00:00:00",
            },
        }

        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value=expected_profile)

        mock_database = MagicMock(spec=AsyncIOMotorDatabase)
        mock_database.__getitem__.return_value = mock_collection

        # Act
        result = await get_aggregated_topic_attributes_repository(
            user_id=user_id,
            database=mock_database,
        )

        # Assert
        assert result == expected_profile
        mock_database.__getitem__.assert_called_once_with("topic_profiles")
        mock_collection.find_one.assert_called_once_with({"user_id": user_id})

    @pytest.mark.asyncio
    async def test_get_topic_profile_repository_profile_not_exists(self) -> None:
        # Arrange
        user_id = "non_existent_user_id"

        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value=None)

        mock_database = MagicMock(spec=AsyncIOMotorDatabase)
        mock_database.__getitem__.return_value = mock_collection

        # Act
        result = await get_aggregated_topic_attributes_repository(
            user_id=user_id,
            database=mock_database,
        )

        # Assert
        assert result is None
        mock_database.__getitem__.assert_called_once_with("topic_profiles")
        mock_collection.find_one.assert_called_once_with({"user_id": user_id})

    @pytest.mark.asyncio
    async def test_get_topic_profile_repository_database_error(self) -> None:
        # Arrange
        user_id = "test_user_id"

        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(side_effect=Exception("Database error"))

        mock_database = MagicMock(spec=AsyncIOMotorDatabase)
        mock_database.__getitem__.return_value = mock_collection

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await get_aggregated_topic_attributes_repository(
                user_id=user_id,
                database=mock_database,
            )

        mock_database.__getitem__.assert_called_once_with("topic_profiles")
        mock_collection.find_one.assert_called_once_with({"user_id": user_id})


class TestUpsertTopicProfileRepository:
    @pytest.mark.asyncio
    async def test_upsert_topic_profile_repository_success(self) -> None:
        # Arrange
        profile_data = {
            "user_id": "test_user_id",
            "topic_attributes": {
                "keywords": [
                    {
                        "name": "python",
                        "weight": 0.8,
                        "updated_at": "2023-01-01T00:00:00",
                    }
                ],
                "entities": [
                    {
                        "category": "language",
                        "name": "python",
                        "weight": 0.8,
                        "updated_at": "2023-01-01T00:00:00",
                    }
                ],
                "sentiments": [
                    {
                        "name": "positive",
                        "weight": 0.9,
                        "updated_at": "2023-01-01T00:00:00",
                    }
                ],
                "updated_at": "2023-01-01T00:00:00",
            },
        }

        mock_collection = MagicMock()
        mock_collection.update_one = AsyncMock()

        mock_database = MagicMock(spec=AsyncIOMotorDatabase)
        mock_database.__getitem__.return_value = mock_collection

        # Act
        await upsert_aggregated_topic_attributes_repository(
            data=profile_data,
            database=mock_database,
        )

        # Assert
        mock_database.__getitem__.assert_called_once_with("topic_profiles")
        mock_collection.update_one.assert_called_once_with(
            {"user_id": profile_data["user_id"]},
            {"$set": profile_data},
            upsert=True,
        )

    @pytest.mark.asyncio
    async def test_upsert_topic_profile_repository_missing_user_id(self) -> None:
        # Arrange
        profile_data = {
            # Missing user_id
            "topic_attributes": {
                "keywords": [],
                "entities": [],
                "sentiments": [],
                "updated_at": "2023-01-01T00:00:00",
            }
        }

        mock_database = MagicMock(spec=AsyncIOMotorDatabase)

        # Act & Assert
        with pytest.raises(ValueError, match="Missing user_id in data"):
            await upsert_aggregated_topic_attributes_repository(
                data=profile_data,
                database=mock_database,
            )

        # Verify database was not accessed
        mock_database.__getitem__.assert_not_called()

    @pytest.mark.asyncio
    async def test_upsert_topic_profile_repository_database_error(self) -> None:
        # Arrange
        profile_data = {
            "user_id": "test_user_id",
            "topic_attributes": {
                "keywords": [],
                "entities": [],
                "sentiments": [],
                "updated_at": "2023-01-01T00:00:00",
            },
        }

        mock_collection = MagicMock()
        mock_collection.update_one = AsyncMock(side_effect=Exception("Database error"))

        mock_database = MagicMock(spec=AsyncIOMotorDatabase)
        mock_database.__getitem__.return_value = mock_collection

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await upsert_aggregated_topic_attributes_repository(
                data=profile_data,
                database=mock_database,
            )

        mock_database.__getitem__.assert_called_once_with("topic_profiles")
        mock_collection.update_one.assert_called_once_with(
            {"user_id": profile_data["user_id"]},
            {"$set": profile_data},
            upsert=True,
        )
