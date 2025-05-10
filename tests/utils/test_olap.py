from unittest.mock import AsyncMock, MagicMock

import pytest
from asynch import Connection, Pool

from src.utils.olap import build_get_clickhouse_connection


class TestBuildGetClickhouseConnection:
    @pytest.mark.asyncio
    async def test_build_get_clickhouse_connection(self) -> None:
        mock_connection = AsyncMock(spec=Connection)
        mock_pool = MagicMock(spec=Pool)
        mock_pool.connection.return_value.__aenter__.return_value = mock_connection

        get_clickhouse_connection = build_get_clickhouse_connection(mock_pool)

        async with get_clickhouse_connection() as connection:
            assert connection == mock_connection

        mock_pool.connection.assert_called_once()

    @pytest.mark.asyncio
    async def test_build_get_clickhouse_connection_handles_exceptions(self) -> None:
        mock_pool = MagicMock(spec=Pool)
        mock_pool.connection.side_effect = Exception("Connection error")

        get_clickhouse_connection = build_get_clickhouse_connection(mock_pool)

        with pytest.raises(Exception, match="Connection error"):
            async with get_clickhouse_connection() as _:
                pass

        mock_pool.connection.assert_called_once()
