from pydantic import BaseModel

from src.schemas import TopicProfileSchema

__all__ = [
    "UserGetDTO",
    "UserOLTPInsertDTO",
]


class UserGetDTO(BaseModel):
    user_id: str
    topic_profile: TopicProfileSchema


class UserOLTPInsertDTO(BaseModel):
    user_id: str
    topic_profile: TopicProfileSchema
