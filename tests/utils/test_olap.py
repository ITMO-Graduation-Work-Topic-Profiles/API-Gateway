from unittest.mock import AsyncMock, MagicMock

import pytest
from asynch import Connection, Pool

from src.utils.olap import (
    build_get_clickhouse_connection,
    get_clickhouse_connection_from_pool,
)


class TestGetClickhouseConnectionFromPool:
    @pytest.mark.asyncio
    async def test_get_clickhouse_connection_from_pool_yields_connection(self) -> None:
        mock_connection = AsyncMock(spec=Connection)
        mock_pool = MagicMock(spec=Pool)
        mock_pool.connection.return_value.__aenter__.return_value = mock_connection

        async with get_clickhouse_connection_from_pool(mock_pool) as actual_connection:
            assert actual_connection == mock_connection


class TestBuildGetClickhouseConnection:
    @pytest.mark.asyncio
    async def test_build_get_clickhouse_connection(self) -> None:
        mock_connection = AsyncMock(spec=Connection)
        mock_pool = MagicMock(spec=Pool)
        mock_pool.connection.return_value.__aenter__.return_value = mock_connection

        connection_instance = build_get_clickhouse_connection(mock_pool)

        async with connection_instance() as connection:
            assert connection == mock_connection

        mock_pool.connection.assert_called_once()

    @pytest.mark.asyncio
    async def test_build_get_clickhouse_connection_handles_exceptions(
        self,
    ) -> None:
        mock_pool = MagicMock(spec=Pool)
        mock_pool.connection.side_effect = Exception("Connection error")

        connection_instance = build_get_clickhouse_connection(mock_pool)

        with pytest.raises(Exception, match="Connection error"):
            async with connection_instance() as _:
                pass

        mock_pool.connection.assert_called_once()
