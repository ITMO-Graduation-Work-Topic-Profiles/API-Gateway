from pydantic import BaseModel

__all__ = [
    "EntityTopicProfileSchema",
    "EntityTopicEventSchema",
]


class EntityTopicProfileSchema(BaseModel):
    category: str
    name: str
    weight: float


class EntityTopicEventSchema(BaseModel):
    category: str
    name: str
    weight: float
