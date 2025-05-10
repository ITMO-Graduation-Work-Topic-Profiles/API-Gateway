from pydantic import BaseModel

from src.schemas import TopicProfileSchema

__all__ = [
    "UserGetDTO",
    "UserCreateDTO",
    "UserOLTPInsertDTO",
]


class UserGetDTO(BaseModel):
    user_id: str
    username: str
    topic_profile: TopicProfileSchema


class UserCreateDTO(BaseModel):
    user_id: str
    username: str


class UserOLTPInsertDTO(BaseModel):
    user_id: str
    topic_profile: TopicProfileSchema
