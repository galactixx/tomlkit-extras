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
    BodyContainer,
    BodyContainerInOrder,
    BodyContainerItems,
    Stylings,
    TOMLDictLike,
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

def container_insert(
    hierarchy: TOMLHierarchy,
    toml_source: TOMLFieldSource,
    insertion: Any,
    position: int
) -> None:
    """
    Inserts an object that is tomlkit compatible based on a container position.
    A "container position" is an integer, indexed at 1, representing the position
    where the insertion object should be placed amongst all other types, including
    stylings (whitespace, comments), within a tomlkit type that supports insertion.
    
    The `toml_source` argument is the base tomlkit instance, and the `hierarchy`
    references the hierarchy relative to, and located within `toml_source` where
    the `insertion` argument will be placed.

    The final level of the `hierarchy` argument must not exist, unless it references
    an array of tables (tomlkit.items.AoT) or array (tomlkit.items.Array). In those
    cases, the `insertion` object will be inserted within the set of existing
    objects.

    Args:
        hierarchy (`TOMLHierarchy`): A `TOMLHierarchy` instance.
        toml_source (`TOMLFieldSource`): A `TOMLFieldSource` instance.
        insertion (Any): An instance of any type.
        position (int): The position of insertion, indexed at 1.
    """
    _insert_into_toml_source(
        inserter=_PositionalInserter(
            toml_source=toml_source,
            hierarchy=hierarchy,
            insertion=insertion,
            position=position,
            by_attribute=False
        )
    )


def attribute_insert(
    hierarchy: TOMLHierarchy,
    toml_source: TOMLFieldSource,
    insertion: Any,
    position: int
) -> None:
    """
    Inserts an object that is tomlkit compatible based on an attribute position.
    An "attribute position" is an integer, indexed at 1, representing the position
    where the insertion object should be placed amongst all other key value pairs
    (fields, tables), within a tomlkit type that supports insertion.
    
    The `toml_source` argument is the base tomlkit instance, and the `hierarchy`
    references the hierarchy relative to, and located within `toml_source` where
    the `insertion` argument will be placed.

    The final level of the `hierarchy` argument must not exist, unless it references
    an array of tables (tomlkit.items.AoT) or array (tomlkit.items.Array). In those
    cases, the `insertion` object will be inserted within the set of existing
    objects.

    Args:
        hierarchy (`TOMLHierarchy`): A `TOMLHierarchy` instance.
        toml_source (`TOMLFieldSource`): A `TOMLFieldSource` instance.
        insertion (Any): An instance of any type.
        position (int): The position of insertion, indexed at 1.
    """
    _insert_into_toml_source(
        inserter=_PositionalInserter(
            toml_source=toml_source,
            hierarchy=hierarchy,
            insertion=insertion,
            position=position,
            by_attribute=True
        )
    )


def general_insert(
    hierarchy: TOMLHierarchy, toml_source: TOMLFieldSource, insertion: Any
) -> None:
    """
    Inserts an object, that is tomlkit compatible, at the bottom of a tomlkit
    type that supports insertion.
    
    The `toml_source` argument is the base tomlkit instance, and the `hierarchy`
    references the hierarchy relative to, and located within `toml_source` where
    the `insertion` argument will be placed.

    The final level of the `hierarchy` argument must not exist, unless it references
    an array of tables (tomlkit.items.AoT) or array (tomlkit.items.Array). In those
    cases, the `insertion` object will be inserted within the set of existing
    objects.

    Args:
        hierarchy (`TOMLHierarchy`): A `TOMLHierarchy` instance.
        toml_source (`TOMLFieldSource`): A `TOMLFieldSource` instance.
        insertion (Any): An instance of any type.
    """
    _insert_into_toml_source(
        inserter=_GeneralInserter(
            toml_source=toml_source, hierarchy=hierarchy, insertion=insertion
        )
    )


def _find_final_toml_level(hierarchy: Hierarchy) -> str:
    """
    A private function that retrieves the last level of a hierarchy given a
    `Hierarchy` instance.
    """
    if hierarchy.hierarchy_depth > 1:
        hierarchy_remaining = hierarchy.attribute
    else:
        hierarchy_remaining = str(hierarchy)
    return hierarchy_remaining


class _BaseItemInserter(ABC):
    """
    A private base abstract class that is an abstract structure which provides
    tools to insert tomlkit.items.Item objects at specific positions within 
    tomlkit types that support insertion.
    """
    def __init__(self, item_to_insert: Tuple[str, items.Item], by_attribute: bool):
        self.item_inserted = False
        self.attribute, self.insertion = item_to_insert
        self.by_attribute = by_attribute

        self.attribute_position = self.container_position = 1

    @abstractmethod
    def add(self, item: items.Item, key: Optional[str] = None) -> None:
        pass

    def insert_attribute(self) -> None:
        self.add(key=self.attribute, item=self.insertion)

    def insert_attribute_in_loop(self, position: int) -> None:
        if (
            (self.attribute_position == position and self.by_attribute) or
            (self.container_position == position and not self.by_attribute)
        ):
            self.insert_attribute()
            self.item_inserted = True
            self.attribute_position += 1


class _DictLikeItemInserter(_BaseItemInserter):
    """
    A sub-class of `_BaseItemInserter` which provides tools to insert tomlkit.items.Item
    objects at specific positions within tomlkit dictionary-like types that support
    insertion.
    """
    def __init__(
        self,
        item_to_insert: Tuple[str, items.Item],
        container: Union[TOMLDocument, items.Table, items.InlineTable],
        by_attribute: bool = True
    ):
        super().__init__(item_to_insert=item_to_insert, by_attribute=by_attribute)
        self.container = container

    def add(self, item: items.Item, key: Optional[str] = None) -> None:
        if key is None:
            self.container.add(cast(Stylings, item))
        else:
            self.container.add(key, item)


class _ListLikeItemInserter(_BaseItemInserter):
    """
    A sub-class of `_BaseItemInserter` which provides tools to insert tomlkit.items.Item
    objects at specific positions within tomlkit list-like types that support insertion.
    """
    def __init__(
        self,
        item_to_insert: Tuple[str, items.Item],
        container: items.Array,
        by_attribute: bool = True
    ):
        super().__init__(item_to_insert=item_to_insert, by_attribute=by_attribute)
        self.container = container

    def add(self, item: items.Item, _: Optional[str] = None) -> None:
        self.container.append(item)


class _BaseInserter(ABC):
    """
    A private base abstract class that is an abstract structure which provides
    tools to run the entire insertion process to insert tomlkit types by
    attribute or container positions within tomlkit types that support insertion.
    """
    def __init__(
        self,
        toml_source: TOMLFieldSource,
        hierarchy: TOMLHierarchy,
        insertion: Any
    ):
        self.toml_source = toml_source

        self.insertion_as_toml_item: items.Item = convert_to_tomlkit_item(value=insertion)
        self.hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
        self.attribute: str = _find_final_toml_level(hierarchy=self.hierarchy_obj)
        
    @abstractmethod
    def array_insert(self, parent: TOMLDictLike) -> None:
        pass

    @abstractmethod
    def insert(self, parent: BodyContainer) -> None:
        pass

    def get_parent_container(self) -> BodyContainer:
        parent_toml = find_parent_toml_source(
            hierarchy=self.hierarchy_obj, toml_source=self.toml_source
        )

        # Ensure the hierarchy does not map to a nested item within an array of tables
        if isinstance(parent_toml, (list, items.AoT)):
            raise InvalidHierarchyError(
                "Hierarchy maps to multiple items, insertion is not possible"
            )

        # Ensure that the hierarchy does not map to a type that does not support insertion
        if not isinstance(parent_toml, INSERTION_TYPES):
            raise InvalidHierarchyError(
                "Hierarchy maps to an instance that does not support insertion"
            )
        
        return parent_toml

    def ensure_array_of_tables_insert(self) -> items.Table:
        if not isinstance(self.insertion_as_toml_item, items.Table):
            raise ValueError(
                "Insertion at top level of an array of tables must be a table instance"
            )
        else:
            return self.insertion_as_toml_item

    def ensure_inline_table_insert(self, parent: BodyContainer) -> None:
        if (
            isinstance(parent, items.InlineTable) and
            isinstance(self.insertion_as_toml_item, (items.AoT, items.Table, items.InlineTable))
        ):
            raise ValueError(
                "Insertion into an inline table must only be simple key-value pairs"
            )

    def possible_array_retrieval(self, parent: BodyContainer) -> BodyContainer:
        if isinstance(parent, DICTIONARY_LIKE_TYPES):
            attribute_toml = parent.get(self.attribute)
            if isinstance(attribute_toml, items.Array):
                parent = attribute_toml
            else:
                assert attribute_toml is None

        return parent


class _GeneralInserter(_BaseInserter):
    """
    A sub-class of `_BaseInserter` which provides tools to insert tomlkit.items.Item
    objects at "generally", AKA at the bottom of tomlkit types that support
    insertion.
    """
    def __init__(
        self,
        toml_source: TOMLFieldSource,
        hierarchy: TOMLHierarchy,
        insertion: Any
    ):
        super().__init__(
            toml_source=toml_source, hierarchy=hierarchy, insertion=insertion
        )

    def array_insert(self, parent: TOMLDictLike) -> None:
        table_to_insert: items.Table = self.ensure_array_of_tables_insert()
        array_of_tables = cast(items.AoT, parent[self.attribute])
        array_of_tables.append(table_to_insert)

    def insert(self, parent: BodyContainer) -> None:
        if isinstance(
            parent, (
                TOMLDocument, items.Table, items.InlineTable, OutOfOrderTableProxy
            )
        ):
            parent[self.attribute] = self.insertion_as_toml_item
        else:
            parent.append(self.insertion_as_toml_item)


class _PositionalInserter(_BaseInserter):
    """
    A sub-class of `_BaseInserter` which provides tools to insert tomlkit.items.Item
    objects at specific positions within tomlkit types that support insertion.
    """
    def __init__(
        self,
        toml_source: TOMLFieldSource,
        hierarchy: TOMLHierarchy,
        insertion: Any,
        position: int,
        by_attribute: bool
    ):
        super().__init__(
            toml_source=toml_source, hierarchy=hierarchy, insertion=insertion
        )
        self.position = position
        self.by_attribute = by_attribute

    @property
    def body_item(self) -> Tuple[str, items.Item]:
        return (self.attribute, self.insertion_as_toml_item)

    def array_insert(self, parent: TOMLDictLike) -> None:
        table_to_insert: items.Table = self.ensure_array_of_tables_insert()
        array_of_tables = cast(items.AoT, parent[self.attribute])
        array_of_tables.insert(self.position - 1, table_to_insert)

    def insert(self, parent: BodyContainer) -> None:
        item_to_insert: Tuple[str, items.Item] = self.body_item
        toml_body_items = copy.deepcopy(get_container_body(toml_source=parent))
        _refresh_container(initial_container=parent)

        container: BodyContainerInOrder
        if isinstance(parent, OutOfOrderTableProxy):
            container = tomlkit.table()
        else:
            container = parent

        inserter: _BaseItemInserter
        if isinstance(container, (TOMLDocument, items.Table, items.InlineTable)):
            inserter = _DictLikeItemInserter(
                item_to_insert=item_to_insert, container=container, by_attribute=self.by_attribute
            )
        else:
            inserter = _ListLikeItemInserter(
                item_to_insert=item_to_insert, container=container, by_attribute=self.by_attribute
            )

        if isinstance(parent, OutOfOrderTableProxy):
            parent.update(container)

        _insert_item_at_position_in_container(
            position=self.position, inserter=inserter, toml_body_items=toml_body_items
        )


def _insert_item_at_position_in_container(
    position: int, inserter: _BaseItemInserter, toml_body_items: BodyContainerItems
) -> None:
    """
    A private function which executes the insertion logic to place a tomlkit.items.Item
    object into a BodyContainer instance at a specific position.
    """
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


def _refresh_container(initial_container: BodyContainer) -> None:
    """
    A private function which "refreshes" or "clears" a `BodyContainer` instance
    of all data, as if starting from a clean slate.
    """
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


def _insert_into_toml_source(inserter: _BaseInserter) -> None:
    """
    A private function which serves as the basis for all three insertion
    operations, `general_insert`, `attribute_insert`, and `container_insert`.
    """
    parent = inserter.get_parent_container()

    if (
        isinstance(parent, DICTIONARY_LIKE_TYPES) and
        isinstance(parent.get(inserter.attribute), items.AoT)
    ):
        inserter.array_insert(parent=parent)
    else:
        parent = inserter.possible_array_retrieval(parent=parent)
        inserter.ensure_inline_table_insert(parent=parent)
        
        inserter.insert(parent=parent)