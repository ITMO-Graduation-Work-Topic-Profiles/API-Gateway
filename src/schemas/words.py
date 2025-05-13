from pydantic import BaseModel

__all__ = ["WordTopicProfileEventSchema"]


class WordTopicProfileEventSchema(BaseModel):
    name: str
    weight: float
