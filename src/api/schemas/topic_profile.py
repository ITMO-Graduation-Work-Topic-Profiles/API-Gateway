from pydantic import BaseModel

from src.api.schemas.entity import EntitySchema
from src.api.schemas.keyword import KeywordSchema
from src.api.schemas.sentiment import SentimentSchema

__all__ = ["TopicProfileSchema"]


class TopicProfileSchema(BaseModel):
    keywords: list[KeywordSchema]
    entities: list[EntitySchema]
    sentiment: SentimentSchema
