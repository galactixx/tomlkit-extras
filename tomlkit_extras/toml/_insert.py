import copy
from abc import ABC, abstractmethod
from typing import (
    Any,
    cast,
    Optional,
    Tuple
)

import tomlkit
from tomlkit.container import OutOfOrderTableProxy
from tomlkit import (
    items, 
    TOMLDocument
)

from tomlkit_extras.toml._retrieval import find_parent_toml_source
from tomlkit_extras._exceptions import InvalidHierarchyError
from tomlkit_extras._hierarchy import (
    Hierarchy,
    standardize_hierarchy
)
from tomlkit_extras._typing import (
    Container,
    ContainerBody,
    ContainerLike,
    TOMLDictLike,
    TOMLHierarchy
)
from tomlkit_extras._utils import (
    complete_clear_array,
    complete_clear_inline_table,
    complete_clear_table,
    complete_clear_toml_document,
    convert_to_tomlkit_item,
    decompose_body_item,
    get_container_body
)

def _find_final_toml_level(hierarchy: Hierarchy) -> str:
    """"""
    if hierarchy.hierarchy_depth > 1:
        hierarchy_parent = Hierarchy.parent_hierarchy(hierarchy=str(hierarchy))
        hierarchy_remaining = cast(Hierarchy, hierarchy.diff(hierarchy=hierarchy_parent))
    else:
        hierarchy_remaining = hierarchy
    return str(hierarchy_remaining)


class BaseInserter(ABC):
    """"""
    def __init__(self, item_to_insert: Tuple[str, items.Item], by_attribute: bool):
        self.item_inserted = False
        self.attribute, self.insertion = item_to_insert
        self.by_attribute = by_attribute

        self.attribute_position = self.container_position = 1

    @abstractmethod
    def add(self, key: Optional[str], item: items.Item) -> None:
        """"""
        pass

    def is_attribute_injection(self, position: int) -> bool:
        """"""
        return (
            (self.attribute_position == position and self.by_attribute) or
            (self.container_position == position and not self.by_attribute)
        )

    def insert_attribute(self) -> None:
        """"""
        self.add(key=self.attribute, item=self.insertion)

    def insert_attribute_in_loop(self, position: int) -> None:
        """"""
        if self.is_attribute_injection(position=position):
            self.insert_attribute()
            self.item_inserted = True
            self.attribute_position += 1


class DictLikeInserter(BaseInserter):
    """"""
    def __init__(
        self,
        item_to_insert: Tuple[str, items.Item],
        container: TOMLDictLike,
        by_attribute: bool = True
    ):
        super().__init__(item_to_insert=item_to_insert, by_attribute=by_attribute)
        self.container = container

    def add(self, key: Optional[str], item: items.Item) -> None:
        return self.container.add(key, item)


class ListLikeInserter(BaseInserter):
    """"""
    def __init__(
        self,
        item_to_insert: Tuple[str, items.Item],
        container: TOMLDictLike,
        by_attribute: bool = True
    ):
        super().__init__(item_to_insert=item_to_insert, by_attribute=by_attribute)
        self.container = container

    def add(self, item: items.Item, _: Optional[str] = None) -> None:
        return self.container.append(item)


def _insert_item_at_position_in_container(
    position: int, inserter: BaseInserter, toml_body_items: ContainerBody
) -> None:
    """"""
    for toml_table_item in toml_body_items:
        item_key, toml_item = decompose_body_item(body_item=toml_table_item)

        if isinstance(toml_item, items.Whitespace):
            toml_item: items.Whitespace = tomlkit.ws(toml_item.value)

        inserter.insert_attribute_in_loop(position=position)

        if item_key is not None:
            inserter.attribute_position += 1

        inserter.add(key=item_key, item=toml_item)
        inserter.container_position += 1

    if not inserter.item_inserted:
        inserter.insert_attribute()


def container_insertion_into_toml_source(
    hierarchy: TOMLHierarchy, toml_source: ContainerLike, insertion: Any, position: int
) -> None:
    """"""
    _positional_insertion_into_toml_source(
        hierarchy=hierarchy, toml_source=toml_source, insertion=insertion, position=position, by_attribute=False
    )


def attribute_insertion_into_toml_source(
    hierarchy: TOMLHierarchy, toml_source: ContainerLike, insertion: Any, position: int
) -> None:
    """"""
    _positional_insertion_into_toml_source(
        hierarchy=hierarchy, toml_source=toml_source, insertion=insertion, position=position, by_attribute=True
    )


def _refresh_container(initial_container: Container) -> None:
    """"""
    match initial_container:
        case items.Table() | OutOfOrderTableProxy():
            complete_clear_table(table=initial_container)
        case items.InlineTable():
            complete_clear_inline_table(table=initial_container)
        case items.Array():
            complete_clear_array(array=initial_container)
        case TOMLDocument():
            complete_clear_toml_document(toml_document=initial_container)
        case _:
            raise ValueError("Type is not a valid container-like structure")


def _positional_insertion_into_toml_source(
    toml_source: ContainerLike, insertion: Any, position: int, by_attribute: bool, hierarchy: Optional[TOMLHierarchy] = None
) -> None:
    """"""
    hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
    attribute: str = _find_final_toml_level(hierarchy=hierarchy_obj)

    insertion_as_toml_item: items.Item = convert_to_tomlkit_item(value=insertion)

    parent_toml = find_parent_toml_source(hierarchy=hierarchy_obj, toml_source=toml_source)

    if isinstance(parent_toml, (list, items.AoT)):
        raise InvalidHierarchyError(
            "Hierarchy maps to multiple items within an array of tables, not a feature of this function"
        )
    
    if (
        attribute in parent_toml and
        isinstance(parent_toml[attribute], items.AoT)
    ):
        if not isinstance(insertion_as_toml_item, items.Table):
            raise ValueError("Insertion at top level of an array of tables must be a table")

        array_of_tables = cast(items.AoT, parent_toml[attribute])
        array_of_tables.insert(position - 1, insertion_as_toml_item)
    else:
        assert attribute not in parent_toml

        if (
            isinstance(parent_toml, items.InlineTable) and
            isinstance(insertion_as_toml_item, (items.AoT, items.Table, items.InlineTable))
        ):
            raise ValueError(
                "Insertion into an inline table must only be simple key-value pairs"
            )

        inserter: BaseInserter

        item_to_insert: Tuple[str, items.Item] = (attribute, insertion_as_toml_item)
        toml_body_items = copy.deepcopy(get_container_body(toml_source=parent_toml))
        _refresh_container(initial_container=parent_toml)

        if isinstance(
            parent_toml,
            (
                TOMLDocument,
                items.Table,
                items.InlineTable,
                OutOfOrderTableProxy
            )
        ):
            inserter = DictLikeInserter(
                item_to_insert=item_to_insert, container=parent_toml, by_attribute=by_attribute
            )
        else:
            inserter = ListLikeInserter(
                item_to_insert=item_to_insert, container=parent_toml, by_attribute=by_attribute
            )

        _insert_item_at_position_in_container(
            position=position, inserter=inserter, toml_body_items=toml_body_items
        )


def general_insertion_into_toml_source(
    hierarchy: TOMLHierarchy, toml_source: TOMLDocument, insertion: Any
) -> None:
    """"""
    hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
    attribute: str = _find_final_toml_level(hierarchy=hierarchy_obj)

    insertion_converted: items.Item = convert_to_tomlkit_item(value=insertion)

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