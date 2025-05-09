from pydantic import BaseModel

__all__ = ["KeywordSchema"]


class KeywordSchema(BaseModel):
    name: str
    weight: float
