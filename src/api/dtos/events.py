import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.utils.dates import utcnow

__all__ = [
    "ContentEventCreateDTO",
    "ContentEventBrokerPublishDTO",
]


class ContentEventCreateDTO(BaseModel):
    user_id: str
    content: str


class ContentEventBrokerPublishDTO(BaseModel):
    content_event_uuid: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: str
    content: str
    timestamp: datetime = Field(default_factory=utcnow)
