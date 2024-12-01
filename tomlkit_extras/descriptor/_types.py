from __future__ import annotations

from dataclasses import dataclass
from typing import (
    cast,
    Optional
)

from tomlkit import items

from tomlkit_extras.descriptor._helpers import get_item_type
from tomlkit_extras._typing import (
    BodyContainerItemDecomposed,
    DescriptorInput,
    Item,
    ParentItem
)

@dataclass
class ItemPosition:
    """"""
    attribute: int
    container: int

    @staticmethod
    def default_position() -> ItemPosition:
        """"""
        return ItemPosition(attribute=1, container=1)

    def update_position(self) -> None:
        """"""
        self.attribute += 1

    def update_body_position(self) -> None:
        """"""
        self.container += 1

    def update_positions(self) -> None:
        self.update_position()
        self.update_body_position()


class ItemInfo:
    """
    """
    def __init__(
        self,
        item_type: Item,
        parent_type: Optional[ParentItem],
        key: str,
        hierarchy: str,
        from_aot: bool
    ) -> None:
        self.item_type = item_type
        self.parent_type = parent_type
        self.key = key
        self.hierarchy = hierarchy
        self.from_aot = from_aot

        self._position: ItemPosition
    
    @property
    def position(self) -> ItemPosition:
        """"""
        return self._position
    
    @position.setter
    def position(self, position: ItemPosition) -> None:
        """"""
        self._position = position

    @classmethod
    def from_parent_type(
        cls,
        key: str,
        hierarchy: str,
        toml_item: DescriptorInput,
        parent_type: Optional[ParentItem] = None,
        from_aot: bool = False
    ) -> ItemInfo:
        """"""
        item_type = get_item_type(toml_item=toml_item)
        return cls(
            item_type=item_type,
            parent_type=parent_type,
            key=key,
            hierarchy=hierarchy,
            from_aot=from_aot
        )

    @classmethod
    def from_body_item(
        cls,
        hierarchy: str, 
        container_info: ItemInfo,
        body_item: BodyContainerItemDecomposed
    ) -> ItemInfo:
        """"""
        item_key, toml_item = body_item
        item_type = get_item_type(toml_item=toml_item)
        parent_type = cast(ParentItem, container_info.item_type)
        key = item_key or ''
        return cls(
            item_type=item_type,
            parent_type=parent_type,
            key=key,
            hierarchy=hierarchy,
            from_aot=container_info.from_aot
        )


class TOMLStatistics:
    """
    """
    def __init__(self) -> None:
        self._number_of_tables = 0
        self._number_of_inline_tables = 0
        self._number_of_aots = 0
        self._number_of_comments = 0
        self._number_of_fields = 0
        self._number_of_arrays = 0

    def add_table(self, table: items.Table) -> None:
        """"""
        if not (isinstance(table, items.Table) and table.is_super_table()):
            self._number_of_tables += 1
            self.add_comment(item=table)

    def add_inline_table(self, table: items.InlineTable) -> None:
        """"""
        self._number_of_inline_tables += 1
        self.add_comment(item=table)

    def add_array(self, item: items.Array) -> None:
        """"""
        self._number_of_arrays += 1
        self.add_comment(item=item)

    def add_aot(self) -> None:
        """"""
        self._number_of_aots += 1

    def add_comment(self, item: items.Item) -> None:
        """"""
        if (
            isinstance(item, items.Comment) or
            (not isinstance(item, items.Whitespace) and item.trivia.comment)
        ):
            self._number_of_comments += 1

    def add_field(self, item: items.Item) -> None:
        """"""
        self._number_of_fields += 1
        self.add_comment(item=item)