from typing import Union

from pyrsistent import pdeque, PDeque
from tomlkit import (
    items, 
    TOMLDocument
)

from tomlkit_extensions._typing import TOMLHierarchy, TOMLSource
from tomlkit_extensions._exceptions import InvalidHierarchyError
from tomlkit_extensions._hierarchy import (
    Hierarchy,
    standardize_hierarchy
)

def _delete_attribute_from_aot(attribute: str, current_source: items.AoT) -> None:
    """"""
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
    """"""
    for table_source in current_source:
        if attribute in table_source:
            next_source = table_source[attribute]
            _recursive_deletion(
                current_source=next_source, hierarchy_queue=hierarchy_queue
            )
            if not next_source:
                del table_source[attribute]


def _recursive_deletion(
    current_source: Union[TOMLDocument, items.Table, items.AoT],
    hierarchy_queue: PDeque[str]
) -> None:
    """"""
    try:
        current_table: str = hierarchy_queue[0]
        hierarchy_queue_new: PDeque[str] = hierarchy_queue.popleft()

        if not hierarchy_queue_new:
            if isinstance(current_source, items.AoT):
                _delete_attribute_from_aot(
                    attribute=current_table, current_source=current_source
                )
            else:
                del current_source[current_table]
        elif isinstance(current_source, items.AoT):
            # Further recursive calls 
            _delete_iteration_for_aot(
                attribute=current_table,
                current_source=current_source,
                hierarchy_queue=hierarchy_queue_new
            )
        else:
            next_source = current_source[current_table]
            _recursive_deletion(
                current_source=next_source, hierarchy_queue=hierarchy_queue_new
            )
            if not next_source:
                del current_source[current_table]
    except KeyError:
        raise InvalidHierarchyError("Hierarchy does not exist in TOML source space")



def delete_from_toml_source(hierarchy: TOMLHierarchy, toml_source: TOMLSource) -> None:
    """"""
    hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)

    hierarchy_queue: PDeque[str] = pdeque(hierarchy_obj.full_hierarchy)
    _recursive_deletion(
        current_source=toml_source, hierarchy_queue=hierarchy_queue
    )
