import typing as tp

from src.dtos import UserGetDTO

__all__ = [
    "get_users_with_topic_profiles_paginated_repository_to_user_get_dto_transformer",
]


def get_users_with_topic_profiles_paginated_repository_to_user_get_dto_transformer(
    sequence: tp.Sequence[tp.Any],
) -> list[UserGetDTO]:
    return list(map(UserGetDTO.model_validate, sequence))
