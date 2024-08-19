from __future__ import annotations
from typing import (
    List,
    Set,
    Union
)

from tomlkit.container import OutOfOrderTableProxy
from tomlkit import items, TOMLDocument

from tomlkit_extras._typing import Item, TOMLValidReturn
from tomlkit_extras._hierarchy import Hierarchy

def find_child_tables(root_hierarchy: str, hierarchies: List[str]) -> Set[str]:
    """"""
    children_hierarchies: Set[str] = set()

    root_hierarchy_obj = Hierarchy.from_str_hierarchy(hierarchy=root_hierarchy) 

    for hierarchy in hierarchies:
        if root_hierarchy_obj.is_child_hierarchy(hierarchy=hierarchy):
            children_hierarchies.add(hierarchy)

    return children_hierarchies


def get_item_type(toml_item: Union[TOMLDocument, TOMLValidReturn]) -> Item:
    """"""
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