from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.entity import EntityTopicProfileSchema
from src.schemas.keyword import KeywordTopicProfileSchema
from src.schemas.sentiment import SentimentTopicProfileSchema
from src.utils.dates import utcnow

__all__ = ["TopicProfileSchema"]


class TopicProfileSchema(BaseModel):
    keywords: list[KeywordTopicProfileSchema] = Field(default_factory=list)
    entities: list[EntityTopicProfileSchema] = Field(default_factory=list)
    sentiment: list[SentimentTopicProfileSchema] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=utcnow)
