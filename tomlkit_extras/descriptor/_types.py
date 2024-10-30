from __future__ import annotations

from dataclasses import dataclass
from typing import (
    cast,
    Dict,
    List,
    Optional
)

from tomlkit import items

from tomlkit_extras.descriptor._helpers import get_item_type
from tomlkit_extras._hierarchy import Hierarchy
from tomlkit_extras._typing import (
    BodyContainerItemDecomposed,
    DescriptorInput,
    Item,
    ParentItem,
    StyleItem,
    Stylings
)
from tomlkit_extras.descriptor._descriptor import (
    ArrayOfTablesDescriptor,
    StyleDescriptor
)

@dataclass
class ArrayOfTablesDescriptors:
    """"""
    aots: List[ArrayOfTablesDescriptor]

    array_indices: Dict[str, int]

    def get_array(self, hierarchy: str) -> ArrayOfTablesDescriptor:
        """"""
        return self.aots[self.array_indices[hierarchy]]

    def update_arrays(self, hierarchy: str, array: ArrayOfTablesDescriptor) -> None:
        """"""
        self.array_indices[hierarchy] += 1
        self.aots.append(array)


@dataclass
class StylingDescriptors:
    """"""
    comments: Dict[str, List[StyleDescriptor]]
    whitespace: Dict[str, List[StyleDescriptor]]

    def update_stylings(
        self, style: Stylings, info: ItemInfo, position: ItemPosition, line_no: int
    ) -> None:
        """"""
        styling_value: str

        if isinstance(style, items.Comment):
            styling_value = style.trivia.comment
            current_source = self.comments
        else:
            styling_value = style.value
            current_source = self.whitespace

        styling_position = StyleDescriptor(
            item_type=cast(StyleItem, info.item_type),
            style=styling_value,
            line_no=line_no,
            container=position.container
        )
        if styling_value not in current_source:
            current_source[styling_value] = [styling_position]
        else:
            current_source[styling_value].append(styling_position)


@dataclass
class ItemInfo:
    """"""
    item_type: Item
    parent_type: Optional[ParentItem]
    key: str
    hierarchy: str

    @property
    def full_hierarchy(self) -> str:
        """"""
        return Hierarchy.create_hierarchy(
            hierarchy=self.hierarchy, attribute=self.key
        )

    @classmethod
    def from_parent_type(
        cls,
        key: str,
        hierarchy: str,
        toml_item: DescriptorInput,
        parent_type: Optional[ParentItem] = None
    ) -> ItemInfo:
        """"""
        item_type = get_item_type(toml_item=toml_item)
        return cls(
            item_type=item_type,
            parent_type=parent_type,
            key=key,
            hierarchy=hierarchy
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
            hierarchy=hierarchy
        )


@dataclass
class ItemPosition:
    """"""
    attribute: int
    container: int

    def update_position(self) -> None:
        """"""
        self.attribute += 1

    def update_body_position(self) -> None:
        """"""
        self.container += 1

    def update_positions(self) -> None:
        self.update_position()
        self.update_body_position()


class TOMLStatistics:
    """"""
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