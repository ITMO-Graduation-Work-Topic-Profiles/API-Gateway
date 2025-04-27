from pydantic import BaseModel, Field

__all__ = ["EntitySchema"]


class EntitySchema(BaseModel):
    name: str
    weight: float = Field(
        ge=0.0,
        le=1.0,
    )
