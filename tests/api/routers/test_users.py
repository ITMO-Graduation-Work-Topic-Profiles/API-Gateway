import typing as tp
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, Request, status
from fastapi.testclient import TestClient
from fastapi_pagination import Page, Params
from starlette.responses import Response

from src.api.routers.users import router
from src.dtos import AggregatedTopicAttributesDTO, UserCreateDTO, UserGetDTO


class TestGetUsersWithTopicProfilesEndpoint:
    @pytest.fixture
    def app(self) -> FastAPI:
        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app: FastAPI) -> TestClient:
        return TestClient(app)

    @pytest.fixture
    def mock_database(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def app_with_database(self, app: FastAPI, mock_database: MagicMock) -> FastAPI:
        app.state.mongo_database = mock_database

        @app.middleware("http")
        async def add_database_to_request(
            request: Request, call_next: tp.Callable[[Request], tp.Awaitable[Response]]
        ) -> Response:
            request.state.mongo_database = app.state.mongo_database
            response = await call_next(request)
            return response

        return app

    @patch("src.api.routers.users.get_users_with_topic_info_paginated_repository")
    def test_get_users_with_topic_profiles_endpoint_success(
        self,
        mock_get_users: AsyncMock,
        client: TestClient,
        app_with_database: FastAPI,
        mock_database: MagicMock,
    ) -> None:
        # Arrange
        mock_users = Page(
            items=[
                UserGetDTO(
                    user_id="user1",
                    username="User 1",
                    topic_attributes=AggregatedTopicAttributesDTO(user_id="user1"),
                ),
                UserGetDTO(
                    user_id="user2",
                    username="User 2",
                    topic_attributes=AggregatedTopicAttributesDTO(user_id="user2"),
                ),
            ],
            total=2,
            page=1,
            size=10,
        )
        mock_get_users.return_value = mock_users

        # Act
        response = client.get("/users")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["total"] == 2
        assert len(response_data["items"]) == 2
        assert response_data["items"][0]["user_id"] == "user1"
        assert response_data["items"][1]["user_id"] == "user2"

        # Verify repository was called with correct parameters
        mock_get_users.assert_called_once()
        call_kwargs = mock_get_users.call_args.kwargs
        assert call_kwargs["keywords"] == []
        assert call_kwargs["entities"] == []
        assert call_kwargs["sentiments"] == []
        assert isinstance(call_kwargs["params"], Params)
        assert call_kwargs["database"] == mock_database

    @patch("src.api.routers.users.get_users_with_topic_info_paginated_repository")
    def test_get_users_with_topic_profiles_endpoint_with_filters(
        self,
        mock_get_users: AsyncMock,
        client: TestClient,
        app_with_database: FastAPI,
        mock_database: MagicMock,
    ) -> None:
        # Arrange
        mock_users = Page(
            items=[
                UserGetDTO(
                    user_id="user1",
                    username="User 1",
                    topic_attributes=AggregatedTopicAttributesDTO(user_id="user1"),
                ),
            ],
            total=1,
            page=1,
            size=10,
        )
        mock_get_users.return_value = mock_users

        # Act
        response = client.get(
            "/users?keywords=python&keywords=fastapi&entities=person&sentiments=positive"
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["total"] == 1
        assert len(response_data["items"]) == 1
        assert response_data["items"][0]["user_id"] == "user1"

        # Verify repository was called with correct parameters
        mock_get_users.assert_called_once()
        call_kwargs = mock_get_users.call_args.kwargs
        assert call_kwargs["keywords"] == ["python", "fastapi"]
        assert call_kwargs["entities"] == ["person"]
        assert call_kwargs["sentiments"] == ["positive"]
        assert isinstance(call_kwargs["params"], Params)
        assert call_kwargs["database"] == mock_database


class TestCreateUserEndpoint:
    @pytest.fixture
    def app(self) -> FastAPI:
        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app: FastAPI) -> TestClient:
        return TestClient(app)

    @pytest.fixture
    def mock_database(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def app_with_database(self, app: FastAPI, mock_database: MagicMock) -> FastAPI:
        app.state.mongo_database = mock_database

        @app.middleware("http")
        async def add_database_to_request(
            request: Request, call_next: tp.Callable[[Request], tp.Awaitable[Response]]
        ) -> Response:
            request.state.mongo_database = app.state.mongo_database
            response = await call_next(request)
            return response

        return app

    @patch("src.api.routers.users.get_user_with_topic_info_repository")
    @patch("src.api.routers.users.insert_user_repository")
    def test_create_user_endpoint_success(
        self,
        mock_insert_user: AsyncMock,
        mock_get_user: AsyncMock,
        client: TestClient,
        app_with_database: FastAPI,
        mock_database: MagicMock,
    ) -> None:
        # Arrange
        user_create_dto = UserCreateDTO(
            user_id="test_user_id",
            username="Test User",
        )

        # First call returns None (user doesn't exist), second call returns the created user
        mock_get_user.side_effect = [
            None,
            {
                "user_id": "test_user_id",
                "username": "Test User",
                "topic_profile": None,
            },
        ]

        # Act
        response = client.post(
            "/users",
            json=user_create_dto.model_dump(),
        )

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["user_id"] == "test_user_id"
        assert response_data["username"] == "Test User"
        assert response_data["aggregated_topic_attributes"] is None

        # Verify repository methods were called with correct parameters
        mock_get_user.assert_called_with(
            user_id="test_user_id",
            database=mock_database,
        )
        mock_insert_user.assert_called_once_with(
            data=user_create_dto.model_dump(),
            database=mock_database,
        )

    @patch("src.api.routers.users.get_user_with_topic_info_repository")
    @patch("src.api.routers.users.insert_user_repository")
    def test_create_user_endpoint_user_already_exists(
        self,
        mock_insert_user: AsyncMock,
        mock_get_user: AsyncMock,
        client: TestClient,
        app_with_database: FastAPI,
        mock_database: MagicMock,
    ) -> None:
        # Arrange
        user_create_dto = UserCreateDTO(
            user_id="existing_user_id",
            username="Existing User",
        )

        # User already exists
        mock_get_user.return_value = {
            "user_id": "existing_user_id",
            "username": "Existing User",
            "topic_profile": None,
        }

        # Act
        response = client.post(
            "/users",
            json=user_create_dto.model_dump(),
        )

        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT
        response_data = response.json()
        assert "detail" in response_data
        assert "existing_user_id" in response_data["detail"]

        # Verify get_user was called but insert_user was not
        mock_get_user.assert_called_once_with(
            user_id="existing_user_id",
            database=mock_database,
        )
        mock_insert_user.assert_not_called()

    def test_create_user_endpoint_validation_error(
        self,
        client: TestClient,
        app_with_database: FastAPI,
    ) -> None:
        # Arrange
        invalid_data = {
            # Missing required username field
            "user_id": "test_user_id",
        }

        # Act
        response = client.post(
            "/users",
            json=invalid_data,
        )

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        response_data = response.json()
        assert "detail" in response_data
        assert any("username" in error["loc"] for error in response_data["detail"])


class TestGetUserByIdEndpoint:
    @pytest.fixture
    def app(self) -> FastAPI:
        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app: FastAPI) -> TestClient:
        return TestClient(app)

    @pytest.fixture
    def mock_database(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def app_with_database(self, app: FastAPI, mock_database: MagicMock) -> FastAPI:
        app.state.mongo_database = mock_database

        @app.middleware("http")
        async def add_database_to_request(
            request: Request, call_next: tp.Callable[[Request], tp.Awaitable[Response]]
        ) -> Response:
            request.state.mongo_database = app.state.mongo_database
            response = await call_next(request)
            return response

        return app

    @patch("src.api.routers.users.get_user_with_topic_info_repository")
    def test_get_user_by_id_endpoint_success(
        self,
        mock_get_user: AsyncMock,
        client: TestClient,
        app_with_database: FastAPI,
        mock_database: MagicMock,
    ) -> None:
        # Arrange
        user_id = "test_user_id"
        mock_get_user.return_value = {
            "user_id": user_id,
            "username": "Test User",
            "aggregated_topic_attributes": {
                "user_id": user_id,
                "keywords": [],
                "entities": [],
                "sentiments": [],
                "updated_at": "2023-01-01T00:00:00",
            },
        }

        # Act
        response = client.get(f"/users/{user_id}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["user_id"] == user_id
        assert response_data["username"] == "Test User"
        assert "aggregated_topic_attributes" in response_data
        assert "keywords" in response_data["aggregated_topic_attributes"]

        # Verify repository was called with correct parameters
        mock_get_user.assert_called_once_with(
            user_id=user_id,
            database=mock_database,
        )

    @patch("src.api.routers.users.get_user_with_topic_info_repository")
    def test_get_user_by_id_endpoint_user_not_found(
        self,
        mock_get_user: AsyncMock,
        client: TestClient,
        app_with_database: FastAPI,
        mock_database: MagicMock,
    ) -> None:
        # Arrange
        user_id = "non_existent_user_id"
        mock_get_user.return_value = None

        # Act
        response = client.get(f"/users/{user_id}")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        response_data = response.json()
        assert "detail" in response_data
        assert user_id in response_data["detail"]

        # Verify repository was called with correct parameters
        mock_get_user.assert_called_once_with(
            user_id=user_id,
            database=mock_database,
        )
