import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas import (
    EntityTopicEventSchema,
    KeywordTopicEventSchema,
    SentimentTopicEventSchema,
)
from src.utils.dates import utcnow

__all__ = [
    "ContentEventCreateDTO",
    "ContentEventBrokerDTO",
    "TopicAttributesEventBrokerDTO",
]


class ContentEventCreateDTO(BaseModel):
    user_id: str
    content: str


class ContentEventBrokerDTO(BaseModel):
    content_event_uuid: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: str
    content: str
    timestamp: datetime = Field(default_factory=utcnow)


class TopicAttributesEventBrokerDTO(BaseModel):
    topic_attributes_event_uuid: uuid.UUID
    content_event_uuid: uuid.UUID
    user_id: str
    keywords: list[KeywordTopicEventSchema]
    entities: list[EntityTopicEventSchema]
    sentiments: list[SentimentTopicEventSchema]
    timestamp: datetime
