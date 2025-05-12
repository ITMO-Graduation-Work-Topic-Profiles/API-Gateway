import typing as tp
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI, Request, status
from fastapi.testclient import TestClient
from starlette.responses import Response

from src.api.routers.events import router
from src.dtos import ContentEventBrokerDTO, ContentEventCreateDTO, MessageResponseDTO


class TestCreateContentEventEndpoint:
    @pytest.fixture
    def app(self) -> FastAPI:
        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app: FastAPI) -> TestClient:
        return TestClient(app)

    @pytest.fixture
    def mock_broker(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def app_with_broker(self, app: FastAPI, mock_broker: AsyncMock) -> FastAPI:
        app.state.broker = mock_broker

        @app.middleware("http")
        async def add_broker_to_request(
            request: Request, call_next: tp.Callable[[Request], tp.Awaitable[Response]]
        ) -> Response:
            request.state.broker = app.state.broker
            response = await call_next(request)
            return response

        return app

    def test_create_content_event_endpoint_success(
        self, client: TestClient, app_with_broker: FastAPI, mock_broker: AsyncMock
    ) -> None:
        content_event_create_dto = ContentEventCreateDTO(
            user_id="test_user_id",
            content="Test content",
        )

        response = client.post(
            "/events/content",
            json=content_event_create_dto.model_dump(),
        )

        assert response.status_code == status.HTTP_202_ACCEPTED
        response_data = response.json()
        assert (
            response_data
            == MessageResponseDTO(
                message="Content event has been queued for creation"
            ).model_dump()
        )

        mock_broker.publish.assert_called_once()
        args, kwargs = mock_broker.publish.call_args
        published_dto, topic = args

        assert isinstance(published_dto, ContentEventBrokerDTO)
        assert published_dto.user_id == content_event_create_dto.user_id
        assert published_dto.content == content_event_create_dto.content
        assert topic == "events-content"

    def test_create_content_event_endpoint_validation_error(
        self, client: TestClient, app_with_broker: FastAPI, mock_broker: AsyncMock
    ) -> None:
        invalid_data = {
            "content": "Test content",
        }

        response = client.post(
            "/events/content",
            json=invalid_data,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        response_data = response.json()
        assert "detail" in response_data
        assert any("user_id" in error["loc"] for error in response_data["detail"])

        mock_broker.publish.assert_not_called()

    def test_create_content_event_endpoint_broker_error(
        self, client: TestClient, app_with_broker: FastAPI, mock_broker: AsyncMock
    ) -> None:
        content_event_create_dto = ContentEventCreateDTO(
            user_id="test_user_id",
            content="Test content",
        )
        mock_broker.publish.side_effect = Exception("Broker error")

        response = client.post(
            "/events/content",
            json=content_event_create_dto.model_dump(),
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

        mock_broker.publish.assert_called_once()
