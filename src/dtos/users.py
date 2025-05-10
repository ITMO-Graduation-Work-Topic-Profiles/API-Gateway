from pydantic import BaseModel

from src.schemas import TopicAttributesSchema

__all__ = [
    "UserGetDTO",
    "UserCreateDTO",
]


class UserGetDTO(BaseModel):
    user_id: str
    username: str
    topic_attributes: TopicAttributesSchema | None = None


class UserCreateDTO(BaseModel):
    user_id: str
    username: str
