from pydantic import BaseModel

__all__ = [
    "KeywordTopicProfileSchema",
    "KeywordTopicEventSchema",
]


class KeywordTopicProfileSchema(BaseModel):
    name: str
    weight: float


class KeywordTopicEventSchema(BaseModel):
    name: str
    weight: float
