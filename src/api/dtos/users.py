from pydantic import BaseModel

from src.api.schemas import TopicProfileSchema

__all__ = ["UserGetDTO"]


class UserGetDTO(BaseModel):
    user_id: str
    topic_profile: TopicProfileSchema
