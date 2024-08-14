from typing import (
    Any,
    cast,
    Optional
)

from tomlkit.container import OutOfOrderTableProxy
from tomlkit import items, TOMLDocument

from tomlkit_extras._utils import convert_to_tomlkit_item
from tomlkit_extras.toml._retrieval import find_parent_toml_source
from tomlkit_extras._exceptions import InvalidHierarchyError
from tomlkit_extras._hierarchy import (
    Hierarchy,
    standardize_hierarchy
)
from tomlkit_extras._typing import (
    ContainerLike, 
    TOMLHierarchy
)

def update_toml_source(
    toml_source: ContainerLike, update: Any, hierarchy: Optional[TOMLHierarchy] = None, full: bool = True
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
        
    update_as_toml_item: items.Item = convert_to_tomlkit_item(value=update)
    
    # Implement a full update
    hierarchy_parent = Hierarchy.parent_hierarchy(hierarchy=str(hierarchy_obj))
    attribute = str(cast(Hierarchy, hierarchy_obj.diff(hierarchy=hierarchy_parent)))
    
    if attribute not in retrieved_from_toml:
        raise InvalidHierarchyError(
            "Hierarchy specified does not exist in TOMLDocument instance"
        )

    if full:
        retrieved_from_toml[attribute] = update_as_toml_item
    else:
        attribute_toml = retrieved_from_toml[attribute]
        if isinstance(attribute_toml, items.Array):
            attribute_toml.add_line(update_as_toml_item)
        elif isinstance(attribute_toml, (
            items.InlineTable,
            items.Table,
            OutOfOrderTableProxy,
            TOMLDocument
        )):
            if not isinstance(update_as_toml_item.unwrap(), dict):
                raise ValueError(
                    "If a dict-like TOML item is being updated, then the instance of the update must "
                    "be a subclass of a dict"
                )
            
            attribute_toml.update(update_as_toml_item)
        elif isinstance(attribute_toml, items.AoT):
            attribute_toml.append(update_as_toml_item)
        else:
            retrieved_from_toml[attribute] = update_as_toml_item