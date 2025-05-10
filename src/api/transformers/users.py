import typing as tp

from src.dtos import UserGetDTO

__all__ = ["get_users_repository_to_user_get_dto_transformer"]


def get_users_repository_to_user_get_dto_transformer(
    sequence: tp.Sequence[tp.Any],
) -> list[UserGetDTO]:
    return [UserGetDTO.model_validate(value) for value in sequence]
