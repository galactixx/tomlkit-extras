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
    """
    A class that stores positional information for a specific `tomlkit` object
    while recursively traversing a TOML structure in the `_generate_descriptor`
    method of `_TOMLParser`.

    The attribute position refers to the position of an item amongst all
    other key value pairs (fields, tables) within the containing object. The
    container position is the position of the item amongst all other types,
    including stylings (whitespace, comments), within the containing object.
    """
    attribute: int
    container: int

    @classmethod
    def default_position(cls) -> ItemPosition:
        """
        Class method that generates a default position where the attribute and
        container positions are both one.
        """
        return ItemPosition(attribute=1, container=1)

    def update_position(self) -> None:
        """Add one to the `attribute` positional property."""
        self.attribute += 1

    def update_body_position(self) -> None:
        """Add one to the `container` positional property."""
        self.container += 1

    def update_positions(self) -> None:
        """Add one to the `attribute` and `container` positional properties."""
        self.update_position()
        self.update_body_position()


class ItemInfo:
    """
    A class that stores general information for a specific `tomlkit` object
    while recursively traversing a TOML structure in the `_generate_descriptor`
    method of `_TOMLParser`.
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
        """Returns the `ItemPosition` object associated with item."""
        return self._position
    
    @position.setter
    def position(self, position: ItemPosition) -> None:
        """Sets the `ItemPosition` object associated with item."""
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
        """
        A class method that creates an `ItemInfo` instance from parent
        information.
        """
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
        """
        A class method that creates an `ItemInfo` instance from the body
        information for an item.
        """
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
    A class that counts and keeps track of the number of different TOML
    structures while recursively traversing a `tomlkit` object in the
    `_generate_descriptor` method of `_TOMLParser`.

    Maintains counts for the following `tomlkit` objects:
    - `tomlkit.items.Table`
    - `tomlkit.items.InlineTable`
    - `tomlkit.items.AoT`
    - `tomlkit.items.Comment`
    - `tomlkit.items.Item` (those that correspond to fields)
    - `tomlkit.items.Array`
    """
    def __init__(self) -> None:
        self.number_of_tables = 0
        self.number_of_inline_tables = 0
        self.number_of_aots = 0
        self.number_of_comments = 0
        self.number_of_fields = 0
        self.number_of_arrays = 0

    def add_table(self, table: items.Table) -> None:
        """
        Given a `tomlkit.items.Table` instance, will check to ensure that it
        is not a super table, and if so will update the table count. In addition,
        will check for a comment associated with the table and if there is one
        the comment count is updated.
        """
        if not (isinstance(table, items.Table) and table.is_super_table()):
            self.number_of_tables += 1
            self.add_comment(item=table)

    def add_inline_table(self, table: items.InlineTable) -> None:
        """
        Given a `tomlkit.items.InlineTable` instance, will update the inline table
        count. In addition, will check for a comment associated with the table and
        if there is one the comment count is updated.
        """
        self.number_of_inline_tables += 1
        self.add_comment(item=table)

    def add_array(self, item: items.Array) -> None:
        """
        Given a `tomlkit.items.Array` instance, will update the array count. In
        addition, will check for a comment associated with the array and if there
        is one the comment count is updated.
        """
        self.number_of_arrays += 1
        self.add_comment(item=item)

    def add_aot(self) -> None:
        """Updates the arrays-of-tables count."""
        self.number_of_aots += 1

    def add_comment(self, item: items.Item) -> None:
        """
        Given a generic `tomlkit.items.Item` instance, will check for a comment
        associated with the item and if there is one the comment count is updated.
        """
        if (
            isinstance(item, items.Comment) or
            (not isinstance(item, items.Whitespace) and item.trivia.comment)
        ):
            self.number_of_comments += 1

    def add_field(self, item: items.Item) -> None:
        """
        Given a generic `tomlkit.items.Item` instance, will update the field count. In
        addition, will check for a comment associated with the field and if there
        is one the comment count is updated.
        """
        self.number_of_fields += 1
        self.add_comment(item=item)