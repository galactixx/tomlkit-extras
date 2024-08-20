import copy
from abc import ABC, abstractmethod
from typing import (
    Any,
    cast,
    Optional,
    Tuple,
    Union
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
from tomlkit_extras._constants import (
    DICTIONARY_LIKE_TYPES,
    INSERTION_TYPES
)
from tomlkit_extras._typing import (
    Container,
    ContainerBody,
    ContainerInOrder,
    Stylings,
    TOMLFieldSource,
    TOMLHierarchy
)
from tomlkit_extras._utils import (
    complete_clear_array,
    complete_clear_out_of_order_table,
    complete_clear_tables,
    complete_clear_toml_document,
    convert_to_tomlkit_item,
    decompose_body_item,
    get_container_body
)

def container_insertion_into_toml_source(
    hierarchy: TOMLHierarchy, toml_source: TOMLFieldSource, insertion: Any, position: int
) -> None:
    """"""
    _positional_insertion_into_toml_source(
        hierarchy=hierarchy, toml_source=toml_source, insertion=insertion, position=position, by_attribute=False
    )


def attribute_insertion_into_toml_source(
    hierarchy: TOMLHierarchy, toml_source: TOMLFieldSource, insertion: Any, position: int
) -> None:
    """"""
    _positional_insertion_into_toml_source(
        hierarchy=hierarchy, toml_source=toml_source, insertion=insertion, position=position, by_attribute=True
    )


def _find_final_toml_level(hierarchy: Hierarchy) -> str:
    """"""
    if hierarchy.hierarchy_depth > 1:
        hierarchy_remaining = hierarchy.attribute
    else:
        hierarchy_remaining = str(hierarchy)
    return hierarchy_remaining


class BaseInserter(ABC):
    """"""
    def __init__(self, item_to_insert: Tuple[str, items.Item], by_attribute: bool):
        self.item_inserted = False
        self.attribute, self.insertion = item_to_insert
        self.by_attribute = by_attribute

        self.attribute_position = self.container_position = 1

    @abstractmethod
    def add(self, item: items.Item, key: Optional[str] = None) -> None:
        """"""
        pass

    def insert_attribute(self) -> None:
        """"""
        self.add(key=self.attribute, item=self.insertion)

    def insert_attribute_in_loop(self, position: int) -> None:
        """"""
        if (
            (self.attribute_position == position and self.by_attribute) or
            (self.container_position == position and not self.by_attribute)
        ):
            self.insert_attribute()
            self.item_inserted = True
            self.attribute_position += 1


class DictLikeInserter(BaseInserter):
    """"""
    def __init__(
        self,
        item_to_insert: Tuple[str, items.Item],
        container: Union[TOMLDocument, items.Table, items.InlineTable],
        by_attribute: bool = True
    ):
        super().__init__(item_to_insert=item_to_insert, by_attribute=by_attribute)
        self.container = container

    def add(self, item: items.Item, key: Optional[str] = None) -> None:
        """"""
        if key is None:
            self.container.add(cast(Stylings, item))
        else:
            self.container.add(key, item)


class ListLikeInserter(BaseInserter):
    """"""
    def __init__(
        self,
        item_to_insert: Tuple[str, items.Item],
        container: items.Array,
        by_attribute: bool = True
    ):
        super().__init__(item_to_insert=item_to_insert, by_attribute=by_attribute)
        self.container = container

    def add(self, item: items.Item, _: Optional[str] = None) -> None:
        """"""
        self.container.append(item)


def _insert_item_at_position_in_container(
    position: int, inserter: BaseInserter, toml_body_items: ContainerBody
) -> None:
    """"""
    for toml_table_item in toml_body_items:
        item_key, toml_item = decompose_body_item(body_item=toml_table_item)

        if isinstance(toml_item, items.Whitespace):
            toml_item = tomlkit.ws(toml_item.value)

        inserter.insert_attribute_in_loop(position=position)

        if item_key is not None:
            inserter.attribute_position += 1

        inserter.add(key=item_key, item=toml_item)
        inserter.container_position += 1

    if not inserter.item_inserted:
        inserter.insert_attribute()


def _refresh_container(initial_container: Container) -> None:
    """"""
    match initial_container:
        case items.Table() | items.InlineTable():
            complete_clear_tables(table=initial_container)
        case OutOfOrderTableProxy():
            complete_clear_out_of_order_table(table=initial_container)
        case items.Array():
            complete_clear_array(array=initial_container)
        case TOMLDocument():
            complete_clear_toml_document(toml_document=initial_container)
        case _:
            raise ValueError("Type is not a valid container-like structure")


def _inline_table_insertion_check(parent: Container, insertion: items.Item) -> None:
    """"""
    if (
        isinstance(parent, items.InlineTable) and
        isinstance(insertion, (items.AoT, items.Table, items.InlineTable))
    ):
        raise ValueError(
            "Insertion into an inline table must only be simple key-value pairs"
        )


def _positional_insertion_into_toml_source(
    toml_source: TOMLFieldSource, hierarchy: TOMLHierarchy, insertion: Any, position: int, by_attribute: bool
) -> None:
    """"""
    insertion_as_toml_item: items.Item = convert_to_tomlkit_item(value=insertion)

    hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
    attribute: str = _find_final_toml_level(hierarchy=hierarchy_obj)

    parent_toml = find_parent_toml_source(hierarchy=hierarchy_obj, toml_source=toml_source)

    # Ensure the hierarchy does not map to multiple items
    if isinstance(parent_toml, (list, items.AoT)):
        raise InvalidHierarchyError("Hierarchy maps to multiple items, insertion is not possible")

    if (
        isinstance(parent_toml, DICTIONARY_LIKE_TYPES) and
        isinstance(parent_toml.get(attribute), items.AoT)
    ):
        if not isinstance(insertion_as_toml_item, items.Table):
            raise ValueError("Insertion at top level of an array of tables must be a table instance")

        array_of_tables = cast(items.AoT, parent_toml[attribute])
        array_of_tables.insert(position - 1, insertion_as_toml_item)
    else:
        if isinstance(parent_toml, DICTIONARY_LIKE_TYPES):
            attribute_toml = parent_toml.get(attribute)
            if isinstance(attribute_toml, items.Array):
                parent_toml = attribute_toml
            else:
                assert attribute_toml is None

        if not isinstance(parent_toml, INSERTION_TYPES):
            raise InvalidHierarchyError("Hierarchy maps to an instance that does not support insertion")

        inserter: BaseInserter
        _inline_table_insertion_check(parent=parent_toml, insertion=insertion_as_toml_item)

        item_to_insert: Tuple[str, items.Item] = (attribute, insertion_as_toml_item)
        toml_body_items = copy.deepcopy(get_container_body(toml_source=parent_toml))
        _refresh_container(initial_container=parent_toml)

        container: ContainerInOrder
        if isinstance(parent_toml, OutOfOrderTableProxy):
            container = tomlkit.table()
        else:
            container = parent_toml

        if isinstance(container, (TOMLDocument, items.Table, items.InlineTable)):
            inserter = DictLikeInserter(item_to_insert=item_to_insert, container=container, by_attribute=by_attribute)
        else:
            inserter = ListLikeInserter(item_to_insert=item_to_insert, container=container, by_attribute=by_attribute)

        if isinstance(parent_toml, OutOfOrderTableProxy):
            parent_toml.update(container)

        _insert_item_at_position_in_container(
            position=position, inserter=inserter, toml_body_items=toml_body_items
        )


def general_insertion_into_toml_source(toml_source: TOMLFieldSource, hierarchy: TOMLHierarchy, insertion: Any) -> None:
    """"""
    hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
    attribute: str = _find_final_toml_level(hierarchy=hierarchy_obj)

    insertion_as_toml_item: items.Item = convert_to_tomlkit_item(value=insertion)

    parent_toml = find_parent_toml_source(hierarchy=hierarchy_obj, toml_source=toml_source)

    # Ensure the hierarchy does not map to a nested item within an array of tables
    if isinstance(parent_toml, (list, items.AoT)):
        raise InvalidHierarchyError("Hierarchy maps to multiple items, insertion is not possible")

    if (
        isinstance(parent_toml, DICTIONARY_LIKE_TYPES) and
        isinstance(parent_toml.get(attribute), items.AoT)
    ):
        if not isinstance(insertion_as_toml_item, items.Table):
            raise ValueError("Insertion at top level of an array must be a table")

        array_of_tables = cast(items.AoT, parent_toml[attribute])
        array_of_tables.append(insertion_as_toml_item)
    else:
        if isinstance(parent_toml, DICTIONARY_LIKE_TYPES):
            attribute_toml = parent_toml.get(attribute)
            if isinstance(attribute_toml, items.Array):
                parent_toml = attribute_toml
            else:
                assert attribute_toml is None

        if not isinstance(parent_toml, INSERTION_TYPES):
            raise InvalidHierarchyError("Hierarchy maps to an instance that does not support insertion")

        _inline_table_insertion_check(parent=parent_toml, insertion=insertion_as_toml_item)
        
        if isinstance(
            parent_toml, (TOMLDocument, items.Table, items.InlineTable, OutOfOrderTableProxy)
        ):
            parent_toml[attribute] = insertion_as_toml_item
        elif isinstance(parent_toml, items.Array):
            parent_toml.append(insertion_as_toml_item)
        else:
            raise ValueError("Type is not a valid container-like structure")