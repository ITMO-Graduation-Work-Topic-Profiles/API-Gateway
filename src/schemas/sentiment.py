from pydantic import BaseModel

__all__ = [
    "SentimentTopicProfileSchema",
    "SentimentTopicEventSchema",
]


class SentimentTopicProfileSchema(BaseModel):
    positive: float | None = None
    neutral: float | None = None
    negative: float | None = None


class SentimentTopicEventSchema(BaseModel):
    name: str
    weight: float
