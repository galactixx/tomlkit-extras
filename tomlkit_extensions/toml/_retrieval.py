from collections import deque
from typing import (
    Any,
    Deque,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    Union
)

from tomlkit import (
    items, 
    TOMLDocument
)

from tomlkit_extensions.exceptions import InvalidHierarchyError
from tomlkit_extensions._utils import (
    decompose_body_item,
    get_container_body
)
from tomlkit_extensions.hierarchy import (
    Hierarchy,
    standardize_hierarchy
)
from tomlkit_extensions.typing import (
    ContainerBody,
    TOMLHierarchy,
    TOMLRetrieval,
    TOMLSource
)

def _get_table_from_aot(current_source: List[items.Item], table: str) -> List[items.Item]:
    """"""
    next_source: List[items.Item] = []

    for source_item in current_source:
        if isinstance(source_item, items.AoT):
            next_source.extend(
                aot_item[table] for aot_item in source_item if table in aot_item
            )
        elif table in source_item:
            next_source.append(source_item[table])
    
    return next_source


def get_positions(hierarchy: TOMLHierarchy, toml_source: TOMLSource) -> Tuple[int, int]:
    """"""
    hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)

    parent_source = find_parent_toml_source(hierarchy=hierarchy_obj, toml_source=toml_source)
    table_body_items: Iterator[ContainerBody] = iter(get_container_body(toml_source=parent_source))

    container_position = attribute_position = 0

    finding_positions = True

    try:
        while finding_positions:
            toml_table_item = next(table_body_items)
            item_key, _ = decompose_body_item(toml_table_item=toml_table_item)

            if item_key is not None:
                attribute_position += 1

            container_position += 1

            if item_key == hierarchy_obj.attribute:
                finding_positions = False 
    except StopIteration:
        raise InvalidHierarchyError(
            "Hierarchy specified does not exist in TOMLDocument instance"
        )

    return attribute_position, container_position


def get_attribute_from_toml_source(
    hierarchy: TOMLHierarchy, toml_source: TOMLSource, array_priority: bool = True
) -> Union[items.Item, List[items.Item]]:
    """"""
    hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)

    hierarchy_of_tables: Deque[str] = deque(hierarchy_obj.full_hierarchy)
    current_source: Union[TOMLDocument, items.Item, List[items.Item]] = toml_source

    try:
        while hierarchy_of_tables:
            table: str = hierarchy_of_tables.popleft()

            if isinstance(current_source, list):
                current_source = _get_table_from_aot(
                    current_source=current_source, table=table
                )
            else:
                current_source = current_source[table]
    except KeyError:
        raise InvalidHierarchyError(
            "Hierarchy specified does not exist in TOMLDocument instance"
        )
    else:
        if not current_source:
            raise InvalidHierarchyError(
                "Hierarchy specified does not exist in TOMLDocument instance"
            )

        if isinstance(current_source, items.AoT) and not array_priority:
            return [aot_table for aot_table in current_source]
        else:
            return current_source
        

def is_toml_instance(
    toml_type: Type[Any], *, hierarchy: TOMLHierarchy, toml_source: TOMLSource, array_priority: bool = True
) -> bool:
    """"""
    toml_items = get_attribute_from_toml_source(
        hierarchy=hierarchy, toml_source=toml_source, array_priority=array_priority
    )

    if (
        not isinstance(toml_items, list) or 
        (isinstance(toml_items, items.AoT) and array_priority)
    ):
        return isinstance(toml_items, toml_type)
    else:
        return all(isinstance(item, toml_type) for item in toml_items)
    

def _find_parent_source(hierarchy: Hierarchy, toml_source: TOMLDocument) -> TOMLRetrieval:
    """"""
    hierarchy_parent = Hierarchy.parent_hierarchy(hierarchy=str(hierarchy))
    return get_attribute_from_toml_source(
        hierarchy=hierarchy_parent, toml_source=toml_source
    )


def find_parent_toml_source(hierarchy: Hierarchy, toml_source: TOMLDocument) -> TOMLRetrieval:
    """"""
    if hierarchy.hierarchy_depth > 1:
        parent_toml = _find_parent_source(hierarchy=hierarchy, toml_source=toml_source)
    else:
        parent_toml = toml_source

    return parent_toml


def find_parent_toml_sources(hierarchy: Hierarchy, toml_source: TOMLDocument) -> Tuple[
    Optional[TOMLRetrieval], TOMLRetrieval
]:
    """"""
    if hierarchy.hierarchy_depth > 1:
        parent_toml = _find_parent_source(hierarchy=hierarchy, toml_source=toml_source)

        if hierarchy.hierarchy_depth > 2:
            grandparent_toml = _find_parent_source(
                hierarchy=Hierarchy.parent_hierarchy(hierarchy=str(hierarchy)),
                toml_source=toml_source
            )
        else:
            grandparent_toml = toml_source
    else:
        grandparent_toml = None
        parent_toml = toml_source

    return grandparent_toml, parent_toml