from typing import Any

import tomlkit
from tomlkit import (
    items, 
    TOMLDocument
)

from tomlkit_extensions._typing import TOMLHierarchy
from tomlkit_extensions.toml._retrieval import find_parent_toml_source
from tomlkit_extensions._exceptions import InvalidHierarchyError
from tomlkit_extensions._hierarchy import (
    Hierarchy,
    standardize_hierarchy
)

def update_non_aot_from_toml_source(
    hierarchy: TOMLHierarchy, toml_source: TOMLDocument, update: Any, full: bool = True
) -> None:
    """"""
    hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)

    hierarchy_remaining, retrieved_from_toml = find_parent_toml_source(
        hierarchy=hierarchy_obj, toml_source=toml_source
    )

    if isinstance(retrieved_from_toml, (list, items.AoT)):
        raise InvalidHierarchyError(
            "Hierarchy maps to an existing array of tables, not a feature of this function"
        )
        
    if not isinstance(update, items.Item):
        update_converted = tomlkit.item(value=update)
    else:
        update_converted = update
    
    # Implement a full update
    final_attribute = str(hierarchy_remaining)
    if full:
        retrieved_from_toml[final_attribute] = update_converted
    else:
        toml_edit_space = retrieved_from_toml[final_attribute]

        if (
            isinstance(update_converted, (items.Table, items.InlineTable)) and
            isinstance(toml_edit_space, (items.Table, items.InlineTable))
        ):
            toml_edit_space.update(update_converted)
        else:
            retrieved_from_toml[final_attribute] = update_converted