import typing as tp

from src.api.dtos import UserGetDTO
from src.api.schemas import TopicProfileSchema

__all__ = ["convert_to_user_get_dto_transformer"]


def convert_to_user_get_dto_transformer(
    sequence: tp.Sequence[tp.Any],
) -> list[UserGetDTO]:
    return [
        UserGetDTO(
            user_id=value.get("user_id"),
            topic_profile=TopicProfileSchema.model_validate(value),
        )
        for value in sequence
    ]
