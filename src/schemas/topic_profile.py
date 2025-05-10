from pydantic import BaseModel

from src.schemas.entity import EntityTopicProfileSchema
from src.schemas.keyword import KeywordTopicProfileSchema
from src.schemas.sentiment import SentimentTopicProfileSchema

__all__ = ["TopicProfileSchema"]


class TopicProfileSchema(BaseModel):
    keywords: list[KeywordTopicProfileSchema]
    entities: list[EntityTopicProfileSchema]
    sentiment: SentimentTopicProfileSchema
