from typing import (
    Any,
    cast,
    Dict,
    List,
    Optional,
    Tuple,
    Union
)

import tomlkit
from tomlkit.container import OutOfOrderTableProxy
from tomlkit import (
    document, 
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
    ContainerItemDecomposed, 
    TOMLHierarchy
)

def from_dict_to_toml_document(dictionary: Dict[str, Any]) -> TOMLDocument:
    """"""
    toml_document: TOMLDocument = document()

    def conversion(toml_source: Dict[str, Any]) -> items.Table:
        toml_table: items.Table = tomlkit.table()

        for source_key, source_value in toml_source.items():
            if isinstance(source_value, dict):
                toml_table[source_key] = conversion(toml_source=source_value)
            else:
                toml_table.update({source_key: source_value})
        
        return toml_table
    
    toml_document.update(conversion(toml_source=dictionary))
    return toml_document


def create_array_of_tables(tables: List[Union[items.Table, Dict[str, Any]]]) -> items.AoT:
    """"""
    array_of_tables: items.AoT = tomlkit.aot()
    for table in tables:
        array_of_tables.append(table)
    return array_of_tables


def create_toml_document(hierarchy: TOMLHierarchy, update: items.Item) -> TOMLDocument:
    """"""
    hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
    source: TOMLDocument = tomlkit.document()

    current_source: Union[items.Item, TOMLDocument] = source
    for table in hierarchy_obj.hierarchy:
        current_source[table] = tomlkit.table()
        current_source = cast(items.Table, current_source[table])

    current_source[hierarchy_obj.attribute] = update

    return source


def partial_clear_toml_document(toml_document: TOMLDocument) -> None:
    """"""
    keys = list(toml_document.keys())
    for key in keys:
        del toml_document[key]


def complete_clear_toml_document(toml_document: TOMLDocument) -> None:
    """"""
    partial_clear_toml_document(toml_document=toml_document)

    # Reset private attributes that store elements within document
    toml_document._map = {}
    toml_document._body = []
    toml_document._parsed = False
    toml_document._table_keys = []


def _reorganize_array(array: items.Array) -> ContainerBody:
    """"""
    array_body_items: ContainerBody = []

    for array_item_group in array._value:
        for array_item in array_item_group:
            array_body_items.append((None, array_item))

    return array_body_items


def get_container_body(toml_source: Container) -> ContainerBody:
    """"""
    if isinstance(toml_source, (items.Table, items.InlineTable)):
        table_body_items = toml_source.value.body
    elif isinstance(toml_source, items.Array):
        table_body_items = _reorganize_array(array=toml_source)
    elif isinstance(toml_source, OutOfOrderTableProxy):
        table_body_items = toml_source._container.body
    elif isinstance(toml_source, TOMLDocument):
        table_body_items = toml_source.body
    else:
        raise ValueError("Type is not a valid container-like structure")

    return table_body_items


def decompose_body_item(
    body_item: Tuple[Optional[items.Key], items.Item]
) -> ContainerItemDecomposed:
    """"""
    item_key: Optional[str] = (
        body_item[0].as_string().strip() if body_item[0] is not None else None
    )
    toml_item: items.Item = body_item[1]
    return item_key, toml_item