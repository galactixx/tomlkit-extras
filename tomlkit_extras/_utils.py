from typing import (
    Any,
    cast,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    Union
)

import tomlkit
from tomlkit.container import OutOfOrderTableProxy
from tomlkit import (
    container,
    items,
    TOMLDocument
)

from tomlkit_extras._hierarchy import (
    Hierarchy,
    standardize_hierarchy
)
from tomlkit_extras._typing import (
    BodyContainer,
    BodyContainerItem,
    BodyContainerItemDecomposed,
    BodyContainerItems,
    TOMLDictLike,
    TOMLHierarchy,
    TOMLSource,
    TOMLValidReturn
)

_VALID_TYPES: Tuple[Type[TOMLSource], ...] = (
    TOMLDocument,
    items.Table,
    items.AoT, 
    OutOfOrderTableProxy
)

def safe_unwrap(structure: TOMLValidReturn) -> Any:
    """
    Safely unwraps a `tomlkit` object, which is the action of returning
    the underlying value that the `tomlkit` type is wrapping.

    This safe logic is needed because even though most types contain an
    `unwrap` method, there are a few in which it is not implemented.

    Args:
        structure (`TOMLValidReturn`): A `TOMLValidReturn` instance.

    Returns:
        Any: Any instance, including pritimitive types and others.
    """
    if isinstance(structure, items.Whitespace):
        return structure.value
    elif isinstance(structure, items.Comment):
        return structure.as_string()
    elif isinstance(structure, bool):
        return structure
    else:
        return structure.unwrap()


def contains_out_of_order_tables(toml_source: TOMLSource) -> bool:
    """
    Given a `TOMLSource` instance, will traverse through the structure
    and determine if there are any out-of-order tables represented by
    instances of `tomlkit.container.OutOfOrderTableProxy`.
    
    Returns a boolean that is True if there are out-of-order tables and
    False if not. 

    Args:
        toml_source (`TOMLSource`): A `TOMLSource` instance.

    Returns:
        bool: A boolean indicating whether there are any out-of-order tables
            located in the TOML structure. 
    """    
    def out_of_order_detect(source: TOMLSource) -> bool:
        # Recursively iterate through dictionary-like tomlkit structures
        if isinstance(source, (TOMLDocument, items.Table)):
            return any(
                out_of_order_detect(source=document_value)
                for _, document_value in source.items()

                # Only recursively traverse through sub-structures if they
                # are tomlkit structures that can contain out-of-order tables
                if isinstance(document_value, _VALID_TYPES)
            )
        # Recursively iterate through list-like tomlkit structures
        # Because items in an array of tables can only be tables, there is
        # no need for a valid type check
        elif isinstance(source, items.AoT):
            return any(
                out_of_order_detect(source=aot_table)
                for aot_table in source
            )
        # Otherwise check if structure is an out-of-order table
        return isinstance(source, OutOfOrderTableProxy)
        
    if not isinstance(toml_source, _VALID_TYPES):
        raise TypeError(
            f'Expected an instance of TOMLSource, but got {type(toml_source).__name__}'
        )
        
    return out_of_order_detect(source=toml_source)


def find_comment_line_no(line_no: int, item: items.Item) -> Optional[int]:
    """
    Given a line number and an `tomlkit.items.Item` instance, will calculate
    the line number in which the comment associated with the item lies on.

    If there is no comment found then will return None.
    
    Args:
        line_no (int): The line number in which the item is located.
        item (`tomlkit.items.Item`): A `tomlkit.items.Item` instance.

    Returns:
        int | None: An integer line number where the comment is located, if
            there is no comment then returns None.
    """
    comment_position: Optional[int]

    if not item.trivia.comment:
        comment_position = None
    else:
        ws_before_comment: str = item.trivia.indent + item.trivia.comment_ws
        num_newlines = ws_before_comment.count('\n')
        comment_position = line_no + num_newlines

    return comment_position


def from_dict_to_toml_document(dictionary: Dict[str, Any]) -> TOMLDocument:
    """
    Converts a dictionary into a `tomlkit.TOMLDocument` instance.

    This function takes a dictionary with string keys and values of any type
    and converts it into a `tomlkit.TOMLDocument`, which is a structured
    representation of TOML data.
    
    Args:
        dictionary (Dict[str, Any]): A dictionary with keys as strings and values
            being of any type.

    Returns:
        `tomlkit.TOMLDocument`: A `tomlkit.TOMLDocument` instance.
    """
    toml_document: TOMLDocument = tomlkit.document()
    for document_key, document_value in dictionary.items():
        toml_document.add(key=document_key, item=document_value)

    return toml_document


def convert_to_tomlkit_item(value: Any) -> items.Item:
    """
    Converts an instance of any type into an `tomlkit.items.Item` instance.

    If the argument is already of type `tomlkit.items.Item`, then the conversion
    is skipped and the input is automatically returned.

    Args:
        value (Any): An instance of any type.
    
    Returns:
        `tomlkit.items.Item`: A `tomlkit.items.Item` instance.
    """
    if not isinstance(value, items.Item):
        value_as_toml_item = tomlkit.item(value=value)
    else:
        value_as_toml_item = value
    return value_as_toml_item


def create_array_of_tables(tables: List[Union[items.Table, Dict[str, Any]]]) -> items.AoT:
    """
    Converts a list of `tomlkit.items.Table` instances or list of dictionaries,
    each with keys as strings and values being of any type, into a
    `tomlkit.items.AoT` instance.

    Args:
        tables (List[`tomlkit.items.Table` | Dict[str, Any]): A list of
            `tomlkit.items.Table` instances or list of dictionaries, each with
            keys as strings and values being of any type

    Returns:
        `tomlkit.items.AoT`: A `tomlkit.items.AoT` instance.
    """
    array_of_tables: items.AoT = tomlkit.aot()
    for table in tables:
        array_of_tables.append(table)
    return array_of_tables


def create_table(fields: Dict[str, Any]) -> items.Table:
    """
    Given a dictionary, will return an `items.Table` instance where the
    fields are are the key-value pairs.

    Args:
        fields (Dict[str, Any]): A general dictionary where the keys are
            strings and values can be of any type.

    Returns:
        `items.Table`: Returns an `items.Table` instance.
    """
    table: items.Table = tomlkit.table()
    table.update(fields)
    return table


def create_inline_table(fields: Dict[str, Any]) -> items.InlineTable:
    """
    Given a dictionary, will return an `items.InlineTable` instance where the
    fields are are the key-value pairs.

    Args:
        fields (Dict[str, Any]): A general dictionary where the keys are
            strings and values can be of any type.

    Returns:
        `items.InlineTable`: Returns an `items.InlineTable` instance.
    """
    inline_table: items.InlineTable = tomlkit.inline_table()
    inline_table.update(fields)
    return inline_table


def create_array(entries: List[Any]) -> items.Array:
    """
    Given a list, will return an `items.Array` instance where the items are
    the entries from the input list.

    Args:
        entries (List[Any]): A general list where the items can be of any type.

    Returns:
        `items.Array`: Returns an `items.Array` instance.
    """
    array: items.Array = tomlkit.array()
    array.extend(entries)
    return array


def create_toml_document(hierarchy: TOMLHierarchy, value: Any) -> TOMLDocument:
    """
    Given a hierarchy of string or `Hierarchy` type, and a value being an
    instance of any type, will create a `tomlkit.TOMLDocument` instance inserting
    the value at the hierarchy, specified. Thus, creating a `tomlkit.TOMLDocument`
    instance around the value.
    
    If the value inserted is not already and instance of `tomlkit.items.Item`,
    will automatically convert into a `tomlkit.items.Item` instance.

    Args:
        hierarchy (`TOMLHierarchy`): A `TOMLHierarchy` instance.
        value (Any): An instance of any type.

    Returns:
        `tomlkit.TOMLDocument`: A `tomlkit.TOMLDocument` instance.
    """
    hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
    source: TOMLDocument = tomlkit.document()

    current_source: Union[items.Table, TOMLDocument] = source
    for table in hierarchy_obj.hierarchy:
        current_source[table] = tomlkit.table()
        current_source = cast(items.Table, current_source[table])

    current_source[hierarchy_obj.attribute] = convert_to_tomlkit_item(value=value)

    return source


def _partial_clear_dict_like_toml_item(toml_source: TOMLDictLike) -> None:
    """
    A private function that deletes all key-value pairs appearing in
    a `TOMLDictLike` instance.
    """
    keys = list(toml_source.keys())
    for key in keys:
        dict.__delitem__(toml_source, key)


def complete_clear_toml_document(toml_document: TOMLDocument) -> None:
    """
    Completely resets a `tomlkit.TOMLDocument` instance, including
    deleting all key-value pairs and all private attributes storing
    data.

    Args:
        toml_document (`tomlkit.TOMLDocument`): A `tomlkit.TOMLDocument` instance.
    """
    _partial_clear_dict_like_toml_item(toml_source=toml_document)

    # Reset private attributes that store elements within document
    toml_document._map = {}
    toml_document._body = []
    toml_document._parsed = False
    toml_document._table_keys = []


def complete_clear_out_of_order_table(table: OutOfOrderTableProxy) -> None:
    """
    Completely resets a `tomlkit.container.OutOfOrderTableProxy` instance,
    including deleting all key-value pairs and all private attributes storing
    data.

    Args:
        table (`tomlkit.container.OutOfOrderTableProxy`):
            A `tomlkit.container.OutOfOrderTableProxy` instance.
    """
    _partial_clear_dict_like_toml_item(toml_source=table)

    # Reset private attributes that store elements within table
    table._container = container.Container()
    table._internal_container = container.Container(True)
    table._tables = []
    table._tables_map = {}


def complete_clear_tables(table: Union[items.Table, items.InlineTable]) -> None:
    """
    Completely resets a `tomlkit.items.Table` or `tomlkit.items.InlineTable`
    instance, including deleting all key-value pairs and all private attributes
    storing data.

    Args:
        table (`tomlkit.items.Table` | `tomlkit.items.InlineTable`): A `tomlkit.items.Table`
            or `tomlkit.items.InlineTable` instance.
    """
    _partial_clear_dict_like_toml_item(toml_source=table)

    # Reset private attributes that store elements within table
    table._value = container.Container()


def complete_clear_array(array: items.Array) -> None:
    """
    Completely resets a `tomlkit.items.Array` instance.

    Args:
        array (`tomlkit.items.Array`): A `tomlkit.items.Array` instance.
    """
    array.clear()


def _reorganize_array(array: items.Array) -> BodyContainerItems:
    """
    A private function which reorganizes a `tomlkit.items.Array` instance and
    returns a `BodyContainerItems` type. This function effectively applies a
    standardization on the body of an array.
    """
    array_body_items: BodyContainerItems = []

    for array_item_group in array._value:
        for array_item in array_item_group:
            array_body_items.append((None, array_item))

    return array_body_items


def get_container_body(toml_source: BodyContainer) -> BodyContainerItems:
    """
    Retrieves the core elements, making up the body of a `BodyContainer` type, 
    and returns a `BodyContainerItems` type.

    Args:
        toml_source (`BodyContainer`): A `BodyContainer` instance.

    Returns:
        `BodyContainerItems`: A `BodyContainerItems` instance.
    """
    match toml_source:
        case items.Table() | items.InlineTable():
            table_body_items = toml_source.value.body
        case items.Array():
            table_body_items = _reorganize_array(array=toml_source)
        case OutOfOrderTableProxy():
            table_body_items = toml_source._container.body
        case TOMLDocument():
            table_body_items = toml_source.body
        case _:
            raise ValueError("Type is not a valid container-like structure")
    return table_body_items


def decompose_body_item(body_item: BodyContainerItem) -> BodyContainerItemDecomposed:
    """
    Decomposes an item, from the body of a `BodyContainer` type, being
    of type `BodyContainerItem`, and returns a `BodyContainerItemDecomposed` type.

    Args:
        body_item (`BodyContainerItem`): A `BodyContainerItem` instance.

    Returns:
        `BodyContainerItemDecomposed`: A `BodyContainerItemDecomposed` instance.
    """
    raw_key = body_item[0]
    item_key: Optional[str] = (
        raw_key.as_string().strip() if raw_key is not None else None
    )
    toml_item: items.Item = body_item[1]
    return item_key, toml_item