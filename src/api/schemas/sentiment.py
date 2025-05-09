from pydantic import BaseModel

__all__ = ["SentimentSchema"]


class SentimentSchema(BaseModel):
    positive: float
    neutral: float
    negative: float
