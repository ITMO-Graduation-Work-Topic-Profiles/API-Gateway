from pydantic import BaseModel

__all__ = ["LabelTopicProfileEventSchema"]


class LabelTopicProfileEventSchema(BaseModel):
    name: str
    weight: float
