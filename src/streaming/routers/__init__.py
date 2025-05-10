from faststream.kafka import KafkaRouter

from .events import router as events_router

__all__ = ["streaming_router"]

streaming_router = KafkaRouter()
streaming_router.include_router(events_router)
