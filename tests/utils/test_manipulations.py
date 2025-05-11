import typing as tp
from dataclasses import dataclass

import pytest

from src.utils.manipulations import split_attributes_from_items


@dataclass
class TestItem:
    name: str
    value: int
    is_active: bool = True


class TestSplitAttributesFromItems:
    def test_split_attributes_from_items_with_single_attribute(self) -> None:
        items = [
            TestItem(name="item1", value=1),
            TestItem(name="item2", value=2),
            TestItem(name="item3", value=3),
        ]

        result = split_attributes_from_items(items, "name")

        assert result == [["item1", "item2", "item3"]]

    def test_split_attributes_from_items_with_multiple_attributes(self) -> None:
        items = [
            TestItem(name="item1", value=1),
            TestItem(name="item2", value=2),
            TestItem(name="item3", value=3),
        ]

        result = split_attributes_from_items(items, "name", "value")

        assert result == [["item1", "item2", "item3"], [1, 2, 3]]

    def test_split_attributes_from_items_with_empty_sequence(self) -> None:
        items: tp.List[TestItem] = []

        result = split_attributes_from_items(items, "name")

        assert result == [[]]

    def test_split_attributes_from_items_with_all_attributes(self) -> None:
        items = [
            TestItem(name="item1", value=1, is_active=True),
            TestItem(name="item2", value=2, is_active=False),
        ]

        result = split_attributes_from_items(items, "name", "value", "is_active")

        assert result == [["item1", "item2"], [1, 2], [True, False]]

    def test_split_attributes_from_items_with_non_existent_attribute(self) -> None:
        items = [
            TestItem(name="item1", value=1),
            TestItem(name="item2", value=2),
        ]

        with pytest.raises(AttributeError):
            split_attributes_from_items(items, "non_existent_attribute")
