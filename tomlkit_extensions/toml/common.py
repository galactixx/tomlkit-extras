from typing import (
    cast,
    List,
    Tuple,
    Union
)

import tomlkit
from tomlkit import (
    items, 
    TOMLDocument
)

from tomlkit_extensions.toml.retrieval import get_attribute_from_toml_source
from tomlkit_extensions.typing import TOMLHierarchy
from tomlkit_extensions.hierarchy import (
    Hierarchy,
    standardize_hierarchy
)

def create_toml_document(hierarchy: TOMLHierarchy, update: items.Item) -> TOMLDocument:
    """"""
    hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
    source: TOMLDocument = tomlkit.document()

    current_source: Union[items.Item, TOMLDocument] = source
    for table in hierarchy_obj.hierarchy:
        current_source[table] = tomlkit.table()
        current_source = cast(items.Table, current_source[table])

    current_source[hierarchy_obj.attribute] = update

    return source


def find_parent_toml_source(
    hierarchy: Hierarchy, toml_source: TOMLDocument
) -> Tuple[Hierarchy, Union[TOMLDocument, items.Item, List[items.Item]]]:
    """"""
    if hierarchy.hierarchy_depth == 1:
        hierarchy_remaining = hierarchy
        retrieved_from_toml = toml_source
    else:
        hierarchy_parent = Hierarchy.parent_hierarchy(hierarchy=str(hierarchy))
        hierarchy_remaining = hierarchy - hierarchy_parent

        retrieved_from_toml = get_attribute_from_toml_source(
            hierarchy=hierarchy_parent, toml_source=toml_source
        )

    return hierarchy_remaining, retrieved_from_toml