import typing as tp
from contextlib import asynccontextmanager

from asynch import Connection, Pool

__all__ = ["build_get_clickhouse_connection", "GetClickhouseConnection"]

GetClickhouseConnection: tp.TypeAlias = tp.Callable[
    [],
    tp.AsyncContextManager[Connection],
]


def build_get_clickhouse_connection(
    pool: Pool,
) -> GetClickhouseConnection:
    @asynccontextmanager
    async def get_clickhouse_connection() -> tp.AsyncIterator[Connection]:
        async with pool.connection() as connection:
            yield connection

    return get_clickhouse_connection
