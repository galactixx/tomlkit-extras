from __future__ import annotations
from typing import (
    List,
    Set,
    Tuple
)

from tomlkit.container import OutOfOrderTableProxy
from tomlkit import items, TOMLDocument

from tomlkit_extensions.typing import TOMLType
from tomlkit_extensions.hierarchy import Hierarchy

def reorganize_array(array: items.Array) -> List[Tuple[None, items.Item]]:
    """"""
    array_body_items: List[Tuple[None, items.Item]] = []

    for array_item_group in array._value:
        for array_item in array_item_group:
            array_body_items.append((None, array_item))

    return array_body_items


def find_nested_tables(root_hierarchy: str, hierarchies: List[str]) -> Set[Hierarchy]:
    """"""
    children_hierarchies: Set[str] = set()

    root_hierarchy_obj = Hierarchy.from_str_hierarchy(hierarchy=root_hierarchy) 

    for hierarchy in hierarchies:
        if root_hierarchy_obj.is_child_hierarchy(hierarchy=hierarchy):
            children_hierarchies.add(hierarchy)

    return children_hierarchies


def get_item_type(toml_item: items.Item) -> TOMLType:
    """"""
    if isinstance(toml_item, TOMLDocument):
        toml_type = 'document'
    elif isinstance(toml_item, items.Table):
        toml_type = 'super-table' if toml_item.is_super_table() else 'table'
    elif isinstance(toml_item, OutOfOrderTableProxy):
        toml_type = 'table'
    elif isinstance(toml_item, items.InlineTable):
        toml_type = 'inline-table'
    elif isinstance(toml_item, items.Comment):
        toml_type = 'comment'
    elif isinstance(toml_item, items.Whitespace):
        toml_type = 'whitespace'
    elif isinstance(toml_item, items.AoT):
        toml_type = 'array-of-tables'
    elif isinstance(toml_item, items.Array):
        toml_type = 'array'
    else:
        toml_type = 'field'

    return toml_type