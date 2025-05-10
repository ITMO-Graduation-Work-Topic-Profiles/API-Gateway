from datetime import datetime

from pydantic import BaseModel, Field

from src.utils.dates import utcnow

__all__ = [
    "EntityTopicProfileSchema",
    "EntityTopicEventSchema",
]


class EntityTopicProfileSchema(BaseModel):
    category: str
    name: str
    weight: float
    updated_at: datetime = Field(default_factory=utcnow)


class EntityTopicEventSchema(BaseModel):
    category: str
    name: str
    weight: float
