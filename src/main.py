import typing as tp
from contextlib import asynccontextmanager
from urllib.parse import urljoin

from beanie import init_beanie
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy import AsyncAdaptedQueuePool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .api.routes import router
from .core.config import Settings
from .databases.oltp.documents import __documents__


@asynccontextmanager
async def lifespan(app: FastAPI) -> tp.AsyncGenerator[None, None]:
    # TODO: Dependency inversion principle has to be applied
    app.state.settings = Settings()
    app.state.sqlalchemy_engine = create_async_engine(
        urljoin(
            app.state.settings.clickhouse.connection.url,
            app.state.settings.clickhouse.database,
        ),
        poolclass=AsyncAdaptedQueuePool,
    )
    app.state.sqlalchemy_session_maker = async_sessionmaker(
        app.state.sqlalchemy_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    app.state.motor_client = AsyncIOMotorClient(app.state.settings.mongo.connection.url)
    await init_beanie(
        database=app.state.motor_client[app.state.settings.mongo.database],
        document_models=__documents__,
    )

    yield

    await app.state.sqlalchemy_engine.dispose()
    app.state.motor_client.close()


app = FastAPI(lifespan=lifespan)

app.include_router(router)

if __name__ == "__main__":
    pass
