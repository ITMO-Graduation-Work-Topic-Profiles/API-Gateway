from datetime import datetime

from pydantic import BaseModel, Field

from src.utils.dates import utcnow

from .aggregated_topic_attributes import AggregatedTopicAttributesDTO

__all__ = [
    "UserGetDTO",
    "UserCreateDTO",
]


class UserDTO:
    user_id: str
    username: str
    updated_at: datetime = Field(default_factory=utcnow)


class UserGetDTO(BaseModel):
    user_id: str
    username: str
    aggregated_topic_attributes: AggregatedTopicAttributesDTO | None = None


class UserCreateDTO(BaseModel):
    user_id: str
    username: str
