from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas import TopicTopicProfileEventSchema
from src.utils.dates import utcnow

__all__ = ["TopicProfileDTO"]


class TopicProfileDTO(BaseModel):
    user_id: str
    topics: list[TopicTopicProfileEventSchema]
    updated_at: datetime = Field(default_factory=utcnow)
