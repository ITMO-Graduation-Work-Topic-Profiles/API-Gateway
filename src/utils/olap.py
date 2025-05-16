import functools
import typing as tp
from contextlib import asynccontextmanager

from asynch import Connection, Pool

__all__ = [
    "build_get_clickhouse_connection",
    "get_clickhouse_connection_from_pool",
    "GetClickhouseConnection",
]

GetClickhouseConnection: tp.TypeAlias = tp.Callable[
    [],
    tp.AsyncContextManager[Connection],
]


@asynccontextmanager
async def get_clickhouse_connection_from_pool(
    pool: Pool,
) -> tp.AsyncIterator[Connection]:
    async with pool.connection() as connection:
        yield connection


def build_get_clickhouse_connection(
    pool: Pool,
) -> GetClickhouseConnection:
    return functools.partial(get_clickhouse_connection_from_pool, pool)
