from pydantic import BaseModel

__all__ = ["SentimentSchema"]


class SentimentSchema(BaseModel):
    positive: float | None = None
    neutral: float | None = None
    negative: float | None = None
