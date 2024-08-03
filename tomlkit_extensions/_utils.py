from typing import (
    Any,
    cast,
    Dict,
    List,
    Union
)

import tomlkit
from tomlkit import (
    document, 
    items,
    TOMLDocument
)

from tomlkit_extensions.hierarchy import (
    Hierarchy,
    standardize_hierarchy
)
from tomlkit_extensions.typing import TOMLHierarchy

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


def clear_toml_document(toml_document: TOMLDocument) -> None:
    """"""
    keys = list(toml_document.keys())
    for key in keys:
        del toml_document[key]
