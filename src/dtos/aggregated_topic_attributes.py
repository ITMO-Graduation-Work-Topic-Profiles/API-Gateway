from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas import (
    EntityTopicProfileSchema,
    KeywordTopicProfileSchema,
    SentimentTopicProfileSchema,
)
from src.utils.dates import utcnow

__all__ = ["AggregatedTopicAttributesDTO"]


class AggregatedTopicAttributesDTO(BaseModel):
    user_id: str
    keywords: list[KeywordTopicProfileSchema] = Field(default_factory=list)
    entities: list[EntityTopicProfileSchema] = Field(default_factory=list)
    sentiments: list[SentimentTopicProfileSchema] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=utcnow)
