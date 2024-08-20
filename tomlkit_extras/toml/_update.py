from typing import Any

from tomlkit.container import OutOfOrderTableProxy
from tomlkit import items, TOMLDocument

from tomlkit_extras._constants import DICTIONARY_LIKE_TYPES
from tomlkit_extras.toml._retrieval import find_parent_toml_source
from tomlkit_extras._exceptions import InvalidHierarchyError
from tomlkit_extras._hierarchy import (
    Hierarchy,
    standardize_hierarchy
)
from tomlkit_extras._typing import ( 
    TOMLHierarchy,
    TOMLSource
)

def update_toml_source(
    toml_source: TOMLSource, update: Any, hierarchy: TOMLHierarchy, full: bool = True
) -> None:
    """"""
    hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)

    retrieved_from_toml = find_parent_toml_source(
        hierarchy=hierarchy_obj, toml_source=toml_source
    )

    if isinstance(retrieved_from_toml, (list, items.AoT)):
        raise InvalidHierarchyError(
            "Hierarchy maps to multiple items within an array of tables, not a feature of this function"
        )
    elif not isinstance(retrieved_from_toml, DICTIONARY_LIKE_TYPES):
        raise ValueError("Type is not a valid container-like structure")
            
    hierarchy_field = hierarchy_obj.attribute
    if hierarchy_field not in retrieved_from_toml:
        raise InvalidHierarchyError(
            "Hierarchy specified does not exist in TOMLDocument instance"
        )

    if full:
        retrieved_from_toml[hierarchy_field] = update
    else:
        attribute_toml = retrieved_from_toml[hierarchy_field]
        if isinstance(attribute_toml, items.Array):
            attribute_toml.add_line(update)
        elif isinstance(
            attribute_toml, (items.InlineTable, items.Table, OutOfOrderTableProxy, TOMLDocument)
        ):
            if not isinstance(update, dict):
                raise ValueError(
                    "If a dict-like TOML item is being updated, then the update instance must "
                    "be a subclass of a dict"
                )
            
            attribute_toml.update(update)
        elif isinstance(attribute_toml, items.AoT):
            attribute_toml.append(update)
        else:
            retrieved_from_toml[hierarchy_field] = update