from datetime import datetime

from pydantic import BaseModel, Field

from src.utils.dates import utcnow

__all__ = [
    "SentimentTopicProfileSchema",
    "SentimentTopicEventSchema",
]


class SentimentTopicProfileSchema(BaseModel):
    name: str
    weight: float
    updated_at: datetime = Field(default_factory=utcnow)


class SentimentTopicEventSchema(BaseModel):
    name: str
    weight: float
