import typing as tp
from contextlib import asynccontextmanager

from fastapi import FastAPI
from faststream.kafka.fastapi import KafkaRouter
from motor.motor_asyncio import AsyncIOMotorClient

from src.api.routers import api_router
from src.core.config import Settings

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> tp.AsyncGenerator[None, None]:
    app.state.settings = settings
    app.state.motor_client = AsyncIOMotorClient(app.state.settings.mongo.connection.url)
    app.state.mongo_database = app.state.motor_client[app.state.settings.mongo.database]

    yield

    app.state.motor_client.close()


faststream_router = KafkaRouter()


app = FastAPI(lifespan=lifespan)

app.include_router(api_router)
app.include_router(faststream_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
