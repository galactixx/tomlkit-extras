from typing import Any, cast

import tomlkit
from tomlkit import (
    items, 
    TOMLDocument
)

from tomlkit_extras._typing import TOMLHierarchy
from tomlkit_extras.toml._retrieval import find_parent_toml_source
from tomlkit_extras._exceptions import InvalidHierarchyError
from tomlkit_extras._hierarchy import (
    Hierarchy,
    standardize_hierarchy
)

def update_toml_source(
    hierarchy: TOMLHierarchy, toml_source: TOMLDocument, update: Any, full: bool = True
) -> None:
    """"""
    hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)

    retrieved_from_toml = find_parent_toml_source(
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
    hierarchy_parent = Hierarchy.parent_hierarchy(hierarchy=str(hierarchy_obj))
    final_attribute = str(cast(Hierarchy, hierarchy_obj.diff(hierarchy=hierarchy_parent)))
    
    if final_attribute not in retrieved_from_toml:
        raise InvalidHierarchyError(
            "Hierarchy specified does not exist in TOMLDocument instance"
        )

    if full:
        retrieved_from_toml[final_attribute] = update_converted
    else:
        toml_edit_space = retrieved_from_toml[final_attribute]

        if (
            isinstance(update_converted, (items.Table, items.InlineTable)) and
            isinstance(toml_edit_space, (items.Table, items.InlineTable))
        ):
            toml_edit_space.update(update_converted)
        elif isinstance(toml_edit_space, items.AoT):
            toml_edit_space.append(update_converted)
        else:
            retrieved_from_toml[final_attribute] = update_converted