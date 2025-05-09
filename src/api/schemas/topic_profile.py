from pydantic import BaseModel

from src.api.schemas.entity import EntitySchema
from src.api.schemas.sentiment import SentimentSchema
from src.api.schemas.topic import TopicSchema

__all__ = ["TopicProfileSchema"]


class TopicProfileSchema(BaseModel):
    topics: list[TopicSchema]
    entities: list[EntitySchema]
    sentiment: SentimentSchema
