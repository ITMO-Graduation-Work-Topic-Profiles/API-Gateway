from pydantic import BaseModel

__all__ = ["LabelTopicProfileEventSchema"]


class LabelTopicProfileEventSchema(BaseModel):
    text: str
    score: float
