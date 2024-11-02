from __future__ import annotations

from dataclasses import dataclass
from typing import (
    Optional,
    Set,
    TYPE_CHECKING,
    Union
)

from tomlkit.container import OutOfOrderTableProxy
from tomlkit import items, TOMLDocument

from tomlkit_extras._typing import Item, TOMLValidReturn
from tomlkit_extras._hierarchy import Hierarchy

if TYPE_CHECKING:
    from tomlkit_extras.descriptor._descriptors import CommentDescriptor

@dataclass
class LineCounter:
    """
    Line counter to keep track of the number of lines seen while
    traversing through and mapping a TOML file within the 
    `TOMLDocumentDescriptor` class.
    """
    line_no: int = 0

    def add_lines(self, lines: int) -> None:
        """Add a custom number of lines."""
        self.line_no += lines

    def add_line(self) -> None:
        """Add one line."""
        self.line_no += 1

    def reset_line_no(self) -> None:
        """Reset the line number to 0."""
        self.line_no = 0


def create_comment_descriptor(item: items.Item, line_no: Optional[int]) -> Optional[CommentDescriptor]:
    """
    A private function that creates a `CommentDescriptor` instance which
    provides detail for a comment that is directly associated with a
    particular field or table.
    
    Can return None if there is no line number corresponding to the item,
    indicating that there is no comment.
    """
    return (
        CommentDescriptor(comment=item.trivia.comment, line_no=line_no)
        if line_no is not None else None
    )


def item_is_table(item_type: Item) -> bool:
    """
    A private function that determines if an `Item` which corresponds to a
    tomlkit instance, is a table.
    """
    return item_type in {'table', 'inline-table'}


def find_child_tables(root_hierarchy: str, hierarchies: Set[str]) -> Set[str]:
    """
    A private function that outputs all child hierarchies of a specific root
    hierarchy, based on a set of string hierarchies.
    """
    children_hierarchies: Set[str] = set()

    root_hierarchy_obj = Hierarchy.from_str_hierarchy(hierarchy=root_hierarchy) 

    for hierarchy in hierarchies:
        if root_hierarchy_obj.is_child_hierarchy(hierarchy=hierarchy):
            children_hierarchies.add(hierarchy)

    return children_hierarchies


def get_item_type(toml_item: Union[TOMLDocument, TOMLValidReturn]) -> Item:
    """
    A private function that will return an Item, corresponding to a string
    literal representing the type of the TOML structure, given a
    tomlkit.TOMLDocument or `TOMLValidReturn` instance

    So, for example, if a tomlkit.TOMLDocument is passed in, then 'document'
    would be returned. If a tomlkit.items.AoT is passed, then 'array-of-tables'
    would output.
    """
    toml_item_type: Item

    match toml_item:
        case TOMLDocument():
            toml_item_type = 'document'
        case items.Table():
            toml_item_type = 'super-table' if toml_item.is_super_table() else 'table'
        case OutOfOrderTableProxy():
            toml_item_type = 'table'
        case items.InlineTable():
            toml_item_type = 'inline-table'
        case items.Comment():
            toml_item_type = 'comment'
        case items.Whitespace():
            toml_item_type = 'whitespace'
        case items.AoT():
            toml_item_type = 'array-of-tables'
        case items.Array():
            toml_item_type = 'array'
        case _:
            toml_item_type = 'field'
    
    return toml_item_type