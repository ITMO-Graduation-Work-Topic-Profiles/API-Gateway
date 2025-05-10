import typing as tp
from contextlib import asynccontextmanager

from asynch import Pool
from fastapi import FastAPI
from faststream.kafka.fastapi import KafkaRouter
from faststream.utils.context.repository import context
from motor.motor_asyncio import AsyncIOMotorClient

from src.api.routers import api_router
from src.core.config import Settings
from src.streaming.routers import streaming_router
from src.utils.olap import build_get_clickhouse_connection

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> tp.AsyncIterator[None]:
    app.state.settings = settings
    app.state.motor_client = AsyncIOMotorClient(app.state.settings.mongo.connection.url)
    app.state.mongo_database = app.state.motor_client[app.state.settings.mongo.database]
    app.state.clickhouse_pool = Pool(dsn=app.state.settings.clickhouse.dsn)
    app.state.get_clickhouse_connection = build_get_clickhouse_connection(
        app.state.clickhouse_pool
    )

    # Necessary to provide faststream context with fastapi state
    context.set_global("state", app.state)

    await app.state.clickhouse_pool.startup()

    yield

    await app.state.clickhouse_pool.shutdown()
    app.state.motor_client.close()


app = FastAPI(lifespan=lifespan)

faststream_router = KafkaRouter(settings.kafka.bootstrap_servers)


app.include_router(api_router)
app.include_router(faststream_router)

faststream_router.include_router(streaming_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
