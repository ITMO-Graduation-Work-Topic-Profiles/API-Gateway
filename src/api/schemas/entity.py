from pydantic import BaseModel

__all__ = ["EntitySchema"]


class EntitySchema(BaseModel):
    category: str
    name: str
    weight: float
