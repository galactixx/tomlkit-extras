from typing import Any

from tomlkit import items

from tomlkit_extras._constants import DICTIONARY_LIKE_TYPES
from tomlkit_extras.toml._retrieval import find_parent_toml_source
from tomlkit_extras._exceptions import (
    InvalidHierarchyUpdateError,
    NotContainerLikeError
)
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
    """
    Given a `TOMLSource` instance, updates a structure at a specific
    hierarchy. This can be either a complete update or partial update,
    determined by the `full` argument.

    If the hierarchy to be updated corresponds to a primitive type, then
    the operation will always be a complete update.

    If `full` is set to True, then the entire structure located at the
    hierarchy will be replaced by what is passed in for the `update` argument.
    Otherwise will only add or overwrite any fields appearing in the `update`
    argument.

    If the hierarchy corresponds to a `tomlkit.items.Array` or `tomlkit.items.AoT`
    and `full` is set to False, then `update` will be appended to the
    bottom.

    Args:
        toml_source (`TOMLSource`): A `TOMLSource` instance.
        update (Any): An instance of any type.
        hierarchy (`TOMLHierarchy`) A `TOMLHierarchy` instance.
        full (bool): A boolean indicating whether the values at the specific
            hierarchy should be completely or partially replaced. Defaults to
            True.
    """
    hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)

    retrieved_from_toml = find_parent_toml_source(
        hierarchy=hierarchy_obj, toml_source=toml_source
    )

    if isinstance(retrieved_from_toml, (list, items.AoT)):
        raise InvalidHierarchyUpdateError(
            'Hierarchy maps to multiple items within an array of tables, '
            'not a feature of this function'
        )
    elif not isinstance(retrieved_from_toml, DICTIONARY_LIKE_TYPES):
        raise NotContainerLikeError("Type is not a valid container-like structure")
            
    hierarchy_field = hierarchy_obj.attribute
    if hierarchy_field not in retrieved_from_toml:
        raise InvalidHierarchyUpdateError(
            'Hierarchy specified does not exist in TOMLSource object'
        )

    # Conditional to distinguish between a complete or partial update
    if full:
        retrieved_from_toml[hierarchy_field] = update
    else:
        attribute_toml = retrieved_from_toml[hierarchy_field]
        if isinstance(attribute_toml, DICTIONARY_LIKE_TYPES):
            if not isinstance(update, dict):
                raise ValueError(
                    'If a dict-like TOML item is being updated, then the update '
                    'instance must be a subclass of a dict'
                )
            
            attribute_toml.update(update)
        elif isinstance(attribute_toml, items.Array):
            attribute_toml.add_line(update)
        elif isinstance(attribute_toml, items.AoT):
            attribute_toml.append(update)
        else:
            retrieved_from_toml[hierarchy_field] = update