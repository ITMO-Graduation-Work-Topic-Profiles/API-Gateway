from pydantic import BaseModel, Field

from .labels import LabelTopicProfileEventSchema
from .words import WordTopicProfileEventSchema

__all__ = ["TopicTopicProfileEventSchema"]


class TopicTopicProfileEventSchema(BaseModel):
    labels: list[LabelTopicProfileEventSchema] = Field(default_factory=list)
    words: list[WordTopicProfileEventSchema] = Field(default_factory=list)
    confidence: float
