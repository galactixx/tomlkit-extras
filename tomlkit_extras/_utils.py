from typing import (
    Any,
    cast,
    Dict,
    List,
    Optional,
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
    Container,
    ContainerBody,
    ContainerBodyItem,
    ContainerItemDecomposed,
    TOMLDictLike,
    TOMLHierarchy
)

def from_dict_to_toml_document(dictionary: Dict[str, Any]) -> TOMLDocument:
    """"""
    toml_document: TOMLDocument = tomlkit.document()
    for document_key, document_value in dictionary.items():
        toml_document.add(key=document_key, item=document_value)

    return toml_document


def convert_to_tomlkit_item(value: Any) -> items.Item:
    """"""
    if not isinstance(value, items.Item):
        value_as_toml_item = tomlkit.item(value=value)
    else:
        value_as_toml_item = value
    return value_as_toml_item


def create_array_of_tables(tables: Union[List[items.Table], List[Dict[str, Any]]]) -> items.AoT:
    """"""
    array_of_tables: items.AoT = tomlkit.aot()
    for table in tables:
        array_of_tables.append(table)
    return array_of_tables


def create_toml_document(hierarchy: TOMLHierarchy, update: items.Item) -> TOMLDocument:
    """"""
    hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
    source: TOMLDocument = tomlkit.document()

    current_source: Union[items.Table, TOMLDocument] = source
    for table in hierarchy_obj.hierarchy:
        current_source[table] = tomlkit.table()
        current_source = cast(items.Table, current_source[table])

    current_source[hierarchy_obj.attribute] = update

    return source


def partial_clear_dict_like_toml_item(toml_source: TOMLDictLike) -> None:
    """"""
    keys = list(toml_source.keys())
    for key in keys:
        dict.__delitem__(toml_source, key)


def complete_clear_toml_document(toml_document: TOMLDocument) -> None:
    """"""
    partial_clear_dict_like_toml_item(toml_source=toml_document)

    # Reset private attributes that store elements within document
    toml_document._map = {}
    toml_document._body = []
    toml_document._parsed = False
    toml_document._table_keys = []


def complete_clear_out_of_order_table(table: OutOfOrderTableProxy) -> None:
    """"""
    partial_clear_dict_like_toml_item(toml_source=table)

    # Reset private attributes that store elements within table
    table._container = container.Container()
    table._internal_container = container.Container(True)
    table._tables = []
    table._tables_map = {}


def complete_clear_tables(table: Union[items.Table, items.InlineTable]) -> None:
    """"""
    partial_clear_dict_like_toml_item(toml_source=table)

    # Reset private attributes that store elements within table
    table._value = container.Container()


def complete_clear_array(array: items.Array) -> None:
    """"""
    array.clear()


def _reorganize_array(array: items.Array) -> ContainerBody:
    """"""
    array_body_items: ContainerBody = []

    for array_item_group in array._value:
        for array_item in array_item_group:
            array_body_items.append((None, array_item))

    return array_body_items


def get_container_body(toml_source: Container) -> ContainerBody:
    """"""
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


def decompose_body_item(body_item: ContainerBodyItem) -> ContainerItemDecomposed:
    """"""
    item_key: Optional[str] = (
        body_item[0].as_string().strip() if body_item[0] is not None else None
    )
    toml_item: items.Item = body_item[1]
    return item_key, toml_item