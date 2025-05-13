from pydantic import BaseModel

__all__ = ["WordTopicProfileEventSchema"]


class WordTopicProfileEventSchema(BaseModel):
    text: str
    score: float
