import typing as tp
from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from .api.routes import router
from .core.config import Settings
from .databases.oltp.documents import __documents__


@asynccontextmanager
async def lifespan(app: FastAPI) -> tp.AsyncGenerator[None, None]:
    # TODO: Dependency inversion principle has to be applied
    app.state.settings = Settings()
    app.state.mongo_client = AsyncIOMotorClient(app.state.settings.mongo.connection.url)
    await init_beanie(
        database=app.state.mongo_client[app.state.settings.mongo.database],
        document_models=__documents__,
    )

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router)

if __name__ == "__main__":
    pass
