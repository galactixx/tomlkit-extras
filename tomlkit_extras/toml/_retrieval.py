from collections import deque
from typing import (
    Any,
    cast,
    Deque,
    Iterator,
    List,
    Literal,
    overload,
    Tuple,
    Type,
    Union
)

from tomlkit.container import OutOfOrderTableProxy
from tomlkit import items

from tomlkit_extras.toml._out_of_order import fix_out_of_order_table
from tomlkit_extras._exceptions import InvalidHierarchyError
from tomlkit_extras._utils import (
    decompose_body_item,
    get_container_body
)
from tomlkit_extras._constants import (
    DICTIONARY_LIKE_TYPES,
    INSERTION_TYPES
)
from tomlkit_extras._hierarchy import (
    Hierarchy,
    standardize_hierarchy
)
from tomlkit_extras._typing import (
    BodyContainerItem,
    Retrieval,
    TOMLFieldSource,
    TOMLHierarchy,
    TOMLSource
)

def _get_table_from_aot(current_source: List[items.Item], table: str) -> List[items.Item]:
    """
    A private function that extracts all items within a tomlkit.items.AoT instance that
    correspond to a specific hierarchy.
    """
    next_source: List[items.Item] = []

    for source_item in current_source:
        if isinstance(source_item, items.AoT):
            next_source.extend(
                aot_item[table] for aot_item in source_item if table in aot_item
            )
        elif isinstance(source_item, DICTIONARY_LIKE_TYPES) and table in source_item:
            next_source.append(source_item[table])
    
    return next_source


def get_positions(hierarchy: TOMLHierarchy, toml_source: TOMLSource) -> Tuple[int, int]:
    """
    Returns both the attribute and container positions of an item located at a specific
    hierarchy within a TOMLSource instance. The attribute and container positions are
    relative to other items within the containing type of the item in question. The attribute
    position refers to the position of item amongst all other key value pairs (fields, tables)
    within the containing class. The container position is the position of the item amongst
    all other types, including stylings (whitespace, comments), within the containing class.

    A tuple is returned, with the first item being an integer representing the attribute
    position, and the second item the container position.
    
    Accepts a TOMLHierarchy instance, being an instance of string or Hierarchy,
    and an instance of TOMLSource.

    Args:
        hierarchy (TOMLHierarchy): A TOMLHierarchy instance.
        toml_source (TOMLSource): A TOMLSource instance.

    Returns:
        Tuple[int, int]: A two-element tuple both elements of integer type. The first item
            representing the attribute position, and the second item the container position.
    """
    hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)

    parent_source = find_parent_toml_source(hierarchy=hierarchy_obj, toml_source=toml_source)
    if not isinstance(parent_source, INSERTION_TYPES):
        raise InvalidHierarchyError("Hierarchy maps to a non-container-like instance")

    table_body_items: Iterator[BodyContainerItem] = iter(get_container_body(toml_source=parent_source))

    container_position = attribute_position = 0
    finding_positions = True

    try:
        while finding_positions:
            toml_table_item = next(table_body_items)
            item_key, _ = decompose_body_item(body_item=toml_table_item)

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


@overload
def get_attribute_from_toml_source(
    hierarchy: TOMLHierarchy, toml_source: TOMLFieldSource, array: bool = True, fix_order: Literal[True] = True
) -> Union[items.Item, List[items.Item]]:
    ...


@overload
def get_attribute_from_toml_source(
    hierarchy: TOMLHierarchy, toml_source: TOMLFieldSource, array: bool = True, fix_order: Literal[False] = False
) -> Retrieval:
    ...


@overload
def get_attribute_from_toml_source(
    hierarchy: TOMLHierarchy, toml_source: TOMLFieldSource, array: bool = True, fix_order: bool = True
) -> object:
    ...


def get_attribute_from_toml_source(
    hierarchy: TOMLHierarchy, toml_source: TOMLFieldSource, array: bool = True, fix_order: bool = False
) -> Retrieval:
    """
    Retrieves and returns the tomlkit type located at a specific hierarchy within a
    TOMLFieldSource instance. If the hierarchy is nested within a tomlkit.items.AoT
    type, then a list with multiple tomlkit types can be returned. Otherwise a
    tomlkit.container.OutOfOrderTableProxy or a subclass of tomlkit.items.Item will be
    returned.

    If the hierarchy does not exist an InvalidHierarchyError will be raised.

    Args:
        hierarchy (TOMLHierarchy): A TOMLHierarchy instance.
        toml_source (TOMLFieldSource): A TOMLFieldSource instance.
        array (bool, optional): If set to False, when a tomlkit.items.AoT instance is to
            be returned, a list of the tables within the array are returned, otherwise it
            will be the AoT instance itself. Defaults to True.
        fix_order (bool, optional): If set to True, will fix any out-of-order tables before
            returning. Defaults to False.

    Returns:
        Retrieval: A Retrieval instance. Either a tomlkit.continer.OutOfOrderTableProxy,
            tomlkit.items.Item or list of tomlkit.items.Item instances.
    """
    hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)

    hierarchy_of_tables: Deque[str] = deque(hierarchy_obj.full_hierarchy)
    current_source: Union[Retrieval, TOMLFieldSource] = toml_source

    try:
        while hierarchy_of_tables:
            table: str = hierarchy_of_tables.popleft()

            if isinstance(current_source, list):
                current_source = _get_table_from_aot(current_source=current_source, table=table)
            else:
                current_source = cast(Retrieval, current_source[table]) # type: ignore[index]
    except KeyError:
        raise InvalidHierarchyError(
            "Hierarchy specified does not exist in TOMLDocument instance"
        )
    else:
        if isinstance(current_source, list) and not current_source:
            raise InvalidHierarchyError(
                "Hierarchy specified does not exist in TOMLDocument instance"
            )

        if isinstance(current_source, items.AoT) and not array:
            return [aot_table for aot_table in current_source]
        elif isinstance(current_source, OutOfOrderTableProxy) and fix_order:
            return fix_out_of_order_table(table=current_source)
        else:
            return cast(Retrieval, current_source)
        

def is_toml_instance(
    _type: Type[Any], *, hierarchy: TOMLHierarchy, toml_source: TOMLFieldSource, array: bool = True, fix_order: bool = False
) -> bool:
    """
    Checks if an item located at a specified hierarchy within a TOMLFieldSource instance
    is of a specific type.
    
    If the hierarchy is nested within a tomlkit.items.AoT type then multiple items will
    correspond to the hierarchy. In this case, each item is tested for type equality.
    
    Args:
        _type (Type[Any]): The type to check.
        hierarchy (TOMLHierarchy): A TOMLHierarchy instance.
        toml_source (TOMLFieldSource): A TOMLFieldSource instance.
        array (bool, optional): If set to False, when a tomlkit.items.AoT instance is to
            be tested, each table in the array is tested for type equality. Otherwise it
            will be the AoT instance itself that is checked. Defaults to True.
        fix_order (bool, optional): If set to True, it will fix any out-of-order tables
            before checking. Defaults to False.

    Returns:
        bool: A boolean indicating whether the item located at the hierarchy is of the
            specified type.
    """
    toml_items = get_attribute_from_toml_source(
        hierarchy=hierarchy, toml_source=toml_source, array=array, fix_order=fix_order
    )

    if (
        not isinstance(toml_items, list) or 
        (isinstance(toml_items, items.AoT) and array)
    ):
        return isinstance(toml_items, _type)
    else:
        return all(isinstance(item, _type) for item in toml_items)
    

def find_parent_toml_source(hierarchy: Hierarchy, toml_source: TOMLFieldSource) -> Union[Retrieval, TOMLFieldSource]:
    """
    A private function that finds the parent of an item located at a specific
    hierarchy within a TOMLFieldSource instance.
    """
    parent_toml: Union[Retrieval, TOMLFieldSource]
    if hierarchy.hierarchy_depth > 1:
        hierarchy_parent = Hierarchy.parent_hierarchy(hierarchy=str(hierarchy))
        parent_toml = get_attribute_from_toml_source(hierarchy=hierarchy_parent, toml_source=toml_source)
    else:
        parent_toml = toml_source

    return parent_toml