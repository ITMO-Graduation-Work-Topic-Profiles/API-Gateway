from pydantic import BaseModel, Field

from src.schemas import TopicAttributesSchema

__all__ = ["TopicProfileDTO"]


class TopicProfileDTO(BaseModel):
    user_id: str
    topic_attributes: TopicAttributesSchema = Field(
        default_factory=TopicAttributesSchema
    )
