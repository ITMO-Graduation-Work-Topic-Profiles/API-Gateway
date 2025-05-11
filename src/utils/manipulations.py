import typing as tp
from operator import attrgetter

__all__ = ["split_attributes_from_items"]


def split_attributes_from_items(
    items: tp.Sequence[tp.Any],
    *attrs: str,
) -> list[list[tp.Any]]:
    return [list(map(attrgetter(attr), items)) for attr in attrs]
