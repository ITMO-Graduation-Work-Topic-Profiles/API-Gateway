from faststream.kafka import KafkaRouter

from .content import router as content_router
from .topic_attributes import router as topic_attributes_router
from .topic_profile import router as topic_profile_router

__all__ = ["streaming_router"]

streaming_router = KafkaRouter()
streaming_router.include_router(topic_profile_router)
streaming_router.include_router(content_router)
streaming_router.include_router(topic_attributes_router)
