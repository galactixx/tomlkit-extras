from typing import (
    cast,
    Union
)

from pyrsistent import pdeque, PDeque
from tomlkit import items, TOMLDocument

from tomlkit_extras._exceptions import InvalidHierarchyError
from tomlkit_extras._hierarchy import (
    Hierarchy,
    standardize_hierarchy
)
from tomlkit_extras._typing import (
    TOMLDictLike,
    TOMLHierarchy,
    TOMLSource,
    TOMLValidReturn
)

def _delete_attribute_from_aot(attribute: str, current_source: items.AoT) -> None:
    """
    A private function that deletes the deepest level of a specified hierarchy. 
    """
    table_deleted = False

    for table_source in current_source[:]:
        if attribute in table_source:
            del table_source[attribute]
            table_deleted = True

        if not table_source:
            current_source.remove(table_source)

    if not table_deleted:
        raise InvalidHierarchyError("Hierarchy does not exist in TOML source space")


def _delete_iteration_for_aot(
    attribute: str, current_source: items.AoT, hierarchy_queue: PDeque[str]
) -> None:
    """
    A private function that executes the recursive deletion for a tomlkit.items.AoT
    instance.
    """
    for table_source in current_source:
        if attribute in table_source:
            next_source = table_source[attribute]
            _recursive_deletion(
                current_source=next_source, hierarchy_queue=hierarchy_queue
            )
            if not next_source:
                del table_source[attribute]


def _recursive_deletion(
    current_source: Union[TOMLDocument, TOMLValidReturn], hierarchy_queue: PDeque[str]
) -> None:
    """
    A private function that executes a recursive deletion of an item within a tomkit
    type, given a hierarchy marking the location of that item.
    """
    try:
        current_table: str = hierarchy_queue[0]
        hierarchy_queue_new: PDeque[str] = hierarchy_queue.popleft()

        if not hierarchy_queue_new:
            if isinstance(current_source, items.AoT):
                _delete_attribute_from_aot(attribute=current_table, current_source=current_source)
            else:
                del cast(TOMLDictLike, current_source)[current_table]
        elif isinstance(current_source, items.AoT):
            _delete_iteration_for_aot(
                attribute=current_table, current_source=current_source, hierarchy_queue=hierarchy_queue_new
            )
        else:
            next_source = cast(TOMLValidReturn, current_source[current_table]) # type: ignore[index]
            _recursive_deletion(
                current_source=next_source, hierarchy_queue=hierarchy_queue_new
            )
            if not next_source:
                del cast(TOMLDictLike, current_source)[current_table]
    except KeyError:
        raise InvalidHierarchyError("Hierarchy does not exist in TOML source space")



def delete_from_toml_source(hierarchy: TOMLHierarchy, toml_source: TOMLSource) -> None:
    """
    Deletes the tomlkit item residing at a speicifc hierarchy within a `TOMLSource`
    instance. In addition, the deletion will continue to cascade backwards as long
    as the last deletion resulted in an empty tomlkit structure.
    
    Accepts a `TOMLHierarchy` instance, being an instance of string or `Hierarchy`,
    and an instance of `TOMLSource`.

    Args:
        hierarchy (`TOMLHierarchy`): A `TOMLHierarchy` instance.
        toml_source (`TOMLSource`): A `TOMLSource` instance.
    """
    hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)

    hierarchy_queue: PDeque[str] = pdeque(hierarchy_obj.full_hierarchy)
    _recursive_deletion(
        current_source=toml_source, hierarchy_queue=hierarchy_queue
    )
