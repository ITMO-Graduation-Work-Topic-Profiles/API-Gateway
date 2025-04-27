import typing as tp

from beanie import Document, Indexed

from ..schemas import EntitySchema, SentimentSchema, TopicSchema
from .mixins import TimestampDocumentMixin

__all__ = ["UserTopicProfileDocument"]


class UserTopicProfileDocument(TimestampDocumentMixin, Document):
    user_id: tp.Annotated[str, Indexed(unique=True)]
    topics: list[TopicSchema]
    entities: list[EntitySchema]
    sentiment: SentimentSchema

    class Settings:
        name = "user_topic_profiles"
        keep_nulls = False
