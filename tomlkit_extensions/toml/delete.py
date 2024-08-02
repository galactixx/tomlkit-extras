from typing import Union

from pyrsistent import pdeque, PDeque
from tomlkit import (
    items, 
    TOMLDocument
)

from tomlkit_extensions.typing import TOMLHierarchy, TOMLSource
from tomlkit_extensions.exceptions import InvalidHierarchyError
from tomlkit_extensions.hierarchy import (
    Hierarchy,
    standardize_hierarchy
)

def delete_from_toml_source(hierarchy: TOMLHierarchy, toml_source: TOMLSource) -> None:
    """"""
    hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)

    def delete(
        current_source: Union[TOMLDocument, items.Table, items.AoT],
        hierarchy_queue: PDeque[str]
    ) -> None:
        """"""
        try:
            current_table: str = hierarchy_queue[0]
            hierarchy_queue_new: PDeque[str] = hierarchy_queue.popleft()

            if not hierarchy_queue_new:
                if isinstance(current_source, items.AoT):
                    table_deleted = False

                    for table_source in current_source:
                        if current_table in table_source:
                            del table_source[current_table]
                            table_deleted = True
                        
                    if not table_deleted:
                        raise InvalidHierarchyError("Hierarchy does not exist in TOML source space")
                else:
                    del current_source[current_table]
            elif isinstance(current_source, items.AoT):
                for table_source in current_source:
                    if current_table in table_source:
                        next_source = table_source[current_table]
                        delete(
                            current_source=next_source, hierarchy_queue=hierarchy_queue_new
                        )
                        if not next_source:
                            del table_source[current_table]
            else:
                next_source = current_source[current_table]
                delete(
                    current_source=next_source, hierarchy_queue=hierarchy_queue_new
                )
                if not next_source:
                    del current_source[current_table]
        except KeyError:
            raise InvalidHierarchyError("Hierarchy does not exist in TOML source space")

    hierarchy_queue: PDeque[str] = pdeque(hierarchy_obj.full_hierarchy)
    delete(
        current_source=toml_source, hierarchy_queue=hierarchy_queue
    )
