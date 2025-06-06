import typing as tp

from src.dtos import UserGetDTO

__all__ = [
    "get_users_with_topic_info_paginated_repository_to_user_get_dto_transformer",
    "get_user_with_topic_info_repository_to_user_get_dto_transformer",
    "get_user_repository_to_user_get_dto_transformer",
]


def get_user_with_topic_info_repository_to_user_get_dto_transformer(
    item: tp.Any,
) -> UserGetDTO:
    # TODO: Refactor
    return UserGetDTO(
        user_id=item["user_id"],
        username=item["username"],
        aggregated_topic_attributes=item["aggregated_topic_attributes"]
        if "aggregated_topic_attributes" in item
        and item["aggregated_topic_attributes"] is not None
        else None,
        topic_profile=item["topic_profile"]
        if "topic_profile" in item and item["topic_profile"]
        else None,
    )


def get_user_repository_to_user_get_dto_transformer(
    item: tp.Any,
) -> UserGetDTO:
    return UserGetDTO(
        user_id=item["user_id"],
        username=item["username"],
        aggregated_topic_attributes=item["aggregated_topic_attributes"]
        if "aggregated_topic_attributes" in item
        and item["aggregated_topic_attributes"] is not None
        else None,
        topic_profile=item["topic_profile"]
        if "topic_profile" in item and item["topic_profile"]
        else None,
    )


def get_users_with_topic_info_paginated_repository_to_user_get_dto_transformer(
    sequence: tp.Sequence[tp.Any],
) -> list[UserGetDTO]:
    return list(
        map(
            get_user_with_topic_info_repository_to_user_get_dto_transformer,
            sequence,
        )
    )
