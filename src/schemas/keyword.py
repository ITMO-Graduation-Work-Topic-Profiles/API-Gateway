from datetime import datetime

from pydantic import BaseModel, Field

from src.utils.dates import utcnow

__all__ = [
    "KeywordTopicProfileSchema",
    "KeywordTopicEventSchema",
]


class KeywordTopicProfileSchema(BaseModel):
    name: str
    weight: float
    updated_at: datetime = Field(default_factory=utcnow)


class KeywordTopicEventSchema(BaseModel):
    name: str
    weight: float
