from typing import (
    Any,
    Dict
)

import tomlkit
from tomlkit import (
    document, 
    items,
    TOMLDocument
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