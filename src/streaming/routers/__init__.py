from faststream.kafka.fastapi import KafkaRouter

from .events import router as events_router

__all__ = [
    "streaming_outer",
    "events_router",
]

streaming_outer = KafkaRouter()
