from typing import (
    Any,
    cast,
    List,
    Optional,
    Tuple,
    Union
)

import tomlkit
from tomlkit import (
    items, 
    TOMLDocument
)

from tomlkit_extensions._utils import (
    complete_clear_toml_document,
    decompose_body_item
)
from tomlkit_extensions._exceptions import InvalidHierarchyError
from tomlkit_extensions._hierarchy import (
    Hierarchy,
    standardize_hierarchy
)
from tomlkit_extensions._typing import (
    Table,
    TOMLHierarchy
)
from tomlkit_extensions.toml._retrieval import (
    find_parent_toml_source,
    find_parent_toml_sources
)

def _convert_to_tomlkit_item(insertion: Any) -> items.Item:
    """"""
    if not isinstance(insertion, items.Item):
        insertion_converted = tomlkit.item(value=insertion)
    else:
        insertion_converted = insertion
    return insertion_converted


def _find_final_toml_level(hierarchy: Hierarchy) -> str:
    """"""
    if hierarchy.hierarchy_depth > 1:
        hierarchy_parent = Hierarchy.parent_hierarchy(hierarchy=str(hierarchy))
        hierarchy_remaining = cast(Hierarchy, hierarchy - hierarchy_parent)
    else:
        hierarchy_remaining = hierarchy
    return str(hierarchy_remaining)


def _insert_item_at_position_in_container(
    position: int,
    item_to_insert: Tuple[str, items.Item],
    toml_body_items: List[Tuple[Optional[items.Key], items.Item]],
    updated_container: Union[TOMLDocument, Table],
    by_attribute: bool = True
) -> None:
    """"""
    item_inserted = False
    attribute, insertion = item_to_insert

    attribute_position = container_position = 1

    for toml_table_item in toml_body_items:
        item_key, toml_item = decompose_body_item(body_item=toml_table_item)

        if isinstance(toml_item, items.Whitespace):
            toml_item: items.Whitespace = tomlkit.ws(toml_item.value)

        if (
            (attribute_position == position and by_attribute) or
            (container_position == position and not by_attribute)
        ):
            updated_container.add(attribute, insertion)
            item_inserted = True
            attribute_position += 1

        if item_key is not None:
            attribute_position += 1

        updated_container.add(item_key, toml_item)
        container_position += 1

    if not item_inserted:
        updated_container.add(attribute, insertion)


def container_insertion_into_toml_source(
    hierarchy: TOMLHierarchy, toml_source: TOMLDocument, insertion: Any, position: int
) -> None:
    """"""
    _positional_insertion_into_toml_source(
        hierarchy=hierarchy, toml_source=toml_source, insertion=insertion, position=position, by_attribute=False
    )


def attribute_insertion_into_toml_source(
    hierarchy: TOMLHierarchy, toml_source: TOMLDocument, insertion: Any, position: int
) -> None:
    """"""
    _positional_insertion_into_toml_source(
        hierarchy=hierarchy, toml_source=toml_source, insertion=insertion, position=position, by_attribute=True
    )


def _positional_insertion_into_toml_source(
    hierarchy: TOMLHierarchy, toml_source: TOMLDocument, insertion: Any, position: int, by_attribute: bool
) -> None:
    """"""
    hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
    attribute: str = _find_final_toml_level(hierarchy=hierarchy_obj)

    insertion_converted: items.Item = _convert_to_tomlkit_item(insertion=insertion)

    grandparent_toml, parent_toml = find_parent_toml_sources(
        hierarchy=hierarchy_obj, toml_source=toml_source
    )

    if isinstance(parent_toml, (list, items.AoT)):
        raise InvalidHierarchyError(
            "Hierarchy maps to an existing array of tables, not a feature of this function"
        )
    
    if (
        attribute in parent_toml and
        isinstance(parent_toml[attribute], items.AoT)
    ):
        if not isinstance(insertion_converted, items.Table):
            raise ValueError("Insertion at top level of an array must be a table")

        array_of_tables = cast(items.AoT, parent_toml[attribute])
        array_of_tables.insert(position - 1, insertion_converted)
    else:
        assert attribute not in parent_toml

        if (
            isinstance(parent_toml, items.InlineTable) and
            isinstance(insertion_converted, (items.AoT, items.Table, items.InlineTable))
        ):
            raise ValueError(
                "Insertion into an inline table must only be simple key-value pairs"
            )
        
        updated_container: Union[TOMLDocument, Table]

        if grandparent_toml is not None:
            updated_container = (
                tomlkit.inline_table() if isinstance(parent_toml, items.InlineTable)
                else tomlkit.table()
            )

            _insert_item_at_position_in_container(
                position=position,
                item_to_insert=(attribute, insertion_converted),
                toml_body_items=parent_toml.value.body,
                updated_container=updated_container,
                by_attribute=by_attribute
            )
            parent_hierarchy = Hierarchy.from_str_hierarchy(
                hierarchy=hierarchy_obj.parent_hierarchy(hierarchy=str(hierarchy_obj))
            )
            grandparent_toml.update({parent_hierarchy.attribute: updated_container})
        else:
            document_body = parent_toml.body.copy()
            complete_clear_toml_document(toml_document=toml_source)

            _insert_item_at_position_in_container(
                position=position,
                item_to_insert=(attribute, insertion_converted),
                toml_body_items=document_body,
                updated_container=toml_source,
                by_attribute=by_attribute
            )


def general_insertion_into_toml_source(
    hierarchy: TOMLHierarchy, toml_source: TOMLDocument, insertion: Any
) -> None:
    """"""
    hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
    attribute: str = _find_final_toml_level(hierarchy=hierarchy_obj)

    insertion_converted: items.Item = _convert_to_tomlkit_item(insertion=insertion)

    parent_toml = find_parent_toml_source(hierarchy=hierarchy_obj, toml_source=toml_source)

    if (
        attribute in parent_toml and
        isinstance(parent_toml[attribute], items.AoT)
    ):
        if not isinstance(insertion_converted, items.Table):
            raise ValueError("Insertion at top level of an array must be a table")

        parent_toml[attribute].append(insertion_converted)
    else:
        assert attribute not in parent_toml

        if (
            isinstance(parent_toml, items.InlineTable) and
            isinstance(insertion_converted, (items.AoT, items.Table, items.InlineTable))
        ):
            raise ValueError(
                "Insertion into an inline table must only be simple key-value pairs"
            )
        
        parent_toml[attribute] = insertion_converted