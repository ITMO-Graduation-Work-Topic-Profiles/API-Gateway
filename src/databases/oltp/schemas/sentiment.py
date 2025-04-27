from pydantic import BaseModel, Field

__all__ = ["SentimentSchema"]


class SentimentSchema(BaseModel):
    positive: float = Field(ge=0.0, le=1.0)
    negative: float = Field(ge=0.0, le=1.0)
    neutral: float = Field(ge=0.0, le=1.0)
