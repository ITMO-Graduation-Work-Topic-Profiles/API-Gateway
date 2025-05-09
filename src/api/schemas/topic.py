from pydantic import BaseModel

__all__ = ["TopicSchema"]


class TopicSchema(BaseModel):
    name: str
    weight: float
