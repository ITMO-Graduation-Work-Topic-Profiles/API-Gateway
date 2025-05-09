from pydantic import BaseModel

from ..schemas import TopicProfileSchema

__all__ = ["UserGetDTO"]


class UserGetDTO(BaseModel):
    user_id: str
    topic_profile: TopicProfileSchema
