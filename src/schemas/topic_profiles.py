from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.entities import EntityTopicProfileSchema
from src.schemas.keywords import KeywordTopicProfileSchema
from src.schemas.sentiments import SentimentTopicProfileSchema
from src.utils.dates import utcnow

__all__ = ["TopicAttributesSchema"]


class TopicAttributesSchema(BaseModel):
    keywords: list[KeywordTopicProfileSchema] = Field(default_factory=list)
    entities: list[EntityTopicProfileSchema] = Field(default_factory=list)
    sentiments: list[SentimentTopicProfileSchema] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=utcnow)
