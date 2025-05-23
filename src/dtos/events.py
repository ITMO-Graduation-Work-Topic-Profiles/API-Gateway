import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas import (
    EntityTopicEventSchema,
    KeywordTopicEventSchema,
    SentimentTopicEventSchema,
    TopicTopicProfileEventSchema,
)
from src.utils.dates import utcnow

__all__ = [
    "ContentEventCreateDTO",
    "ContentEventDTO",
    "ContentEventBrokerDTO",
    "TopicAttributesEventBrokerDTO",
    "TopicProfileEventBrokerDTO",
    "UserContentEventDTO",
]


class ContentEventCreateDTO(BaseModel):
    user_id: str
    content: str


class ContentEventBrokerDTO(BaseModel):
    content_event_uuid: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: str
    content: str
    timestamp: datetime = Field(default_factory=utcnow)


class ContentEventDTO(BaseModel):
    content_event_uuid: uuid.UUID
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


class TopicProfileEventBrokerDTO(BaseModel):
    topic_profile_event_uuid: uuid.UUID
    user_content_event_uuid: uuid.UUID
    user_id: str
    topics: list[TopicTopicProfileEventSchema]
    timestamp: datetime


class UserContentEventDTO(BaseModel):
    user_content_event_uuid: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: str
    content_events: list[ContentEventDTO]
    timestamp: datetime = Field(default_factory=utcnow)
