import typing as tp

from src.dtos import UserGetDTO

__all__ = [
    "get_users_with_topic_profiles_paginated_repository_to_user_get_dto_transformer",
    "get_user_with_topic_profile_repository_to_user_get_dto_transformer",
]


def get_user_with_topic_profile_repository_to_user_get_dto_transformer(
    item: tp.Any,
) -> UserGetDTO:
    return UserGetDTO(
        user_id=item["user_id"],
        username=item["username"],
        # Nested structure because of unwind on the pipeline level
        topic_profile=item["topic_profile"]["topic_profile"],
    )


def get_users_with_topic_profiles_paginated_repository_to_user_get_dto_transformer(
    sequence: tp.Sequence[tp.Any],
) -> list[UserGetDTO]:
    return list(
        map(
            get_user_with_topic_profile_repository_to_user_get_dto_transformer,
            sequence,
        )
    )
