from faststream.kafka import KafkaRouter

__all__ = ["router"]

router = KafkaRouter(prefix="events-")
