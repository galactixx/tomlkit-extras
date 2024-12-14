import copy
from abc import ABC, abstractmethod
import datetime
import warnings
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

from tomlkit_extras.toml._retrieval import get_attribute_from_toml_source
from tomlkit_extras._exceptions import (
    KeyNotProvidedError,
    TOMLInsertionError
)
from tomlkit_extras._hierarchy import (
    Hierarchy,
    standardize_hierarchy
)
from tomlkit_extras._constants import DICTIONARY_LIKE_TYPES
from tomlkit_extras._typing import (
    BodyContainer,
    BodyContainerInOrder,
    BodyContainerItemDecomposed,
    BodyContainerItems,
    ContainerLike,
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

_VALID_ARRAY_OR_INLINE_TYPES = (
    bool,                  # boolean
    int,                   # integer
    float,                 # float
    str,                   # string
    datetime.datetime,     # offset_date_time / local_date_time
    datetime.date,         # local_date
    datetime.time,         # local_time
    items.Array,           # array
    items.InlineTable      # inline_table
)

def container_insert(
    toml_source: TOMLFieldSource,
    insertion: Any,
    position: int,
    hierarchy: Optional[TOMLHierarchy] = None,
    key: Optional[str] = None
) -> None:
    """
    Inserts an object that is tomlkit compatible based on a container
    position. A "container position" is an integer, indexed at 1,
    representing the position where the insertion object should be placed
    amongst all other types, including stylings (whitespace, comments),
    within a tomlkit type that supports insertion.
    
    The `toml_source` argument is the base tomlkit instance, and the
    `hierarchy` references the hierarchy relative to, and located within
    `toml_source` where the `insertion` argument will be placed.
    
    The `hierarchy` argument must exist within the `tomlkit` object,
    unless it is None. If this argument is passed in as None, then the
    insertion will occur at the top-level space of the `tomlkit` object.

    The `key` argument is the string key corresponding to the data that
    is being inserted. This should always be a string unless inserting in
    a array or array of tables. In those cases, a `key` should not be
    provided and will default to None.

    Args:
        toml_source (`TOMLFieldSource`): A `TOMLFieldSource` instance.
        insertion (Any): An instance of any type.
        position (int): The position of insertion, indexed at 1.
        hierarchy (`TOMLHierarchy` | None): A `TOMLHierarchy` instance or
            None. Defaults to None.
        key (str | None): A string corresponding to the key of data that
            is being inserted. Can also be None. Defaults to None.
    """
    _insert_into_toml_source(
        inserter=_PositionalInserter(
            toml_source=toml_source,
            hierarchy=hierarchy,
            key=key,
            insertion=insertion,
            position=position,
            by_attribute=False
        )
    )


def attribute_insert(
    toml_source: TOMLFieldSource,
    insertion: Any,
    position: int,
    hierarchy: Optional[TOMLHierarchy] = None,
    key: Optional[str] = None
) -> None:
    """
    Inserts an object that is tomlkit compatible based on a container
    position. A "container position" is an integer, indexed at 1,
    representing the position where the insertion object should be placed
    amongst all other types, including stylings (whitespace, comments),
    within a tomlkit type that supports insertion.
    
    The `toml_source` argument is the base tomlkit instance, and the
    `hierarchy` references the hierarchy relative to, and located within
    `toml_source` where the `insertion` argument will be placed.
    
    The `hierarchy` argument must exist within the `tomlkit` object,
    unless it is None. If this argument is passed in as None, then the
    insertion will occur at the top-level space of the `tomlkit` object.

    The `key` argument is the string key corresponding to the data that
    is being inserted. This should always be a string unless inserting in
    a array or array of tables. In those cases, a `key` should not be
    provided and will default to None.

    Args:
        toml_source (`TOMLFieldSource`): A `TOMLFieldSource` instance.
        insertion (Any): An instance of any type.
        position (int): The position of insertion, indexed at 1.
        hierarchy (`TOMLHierarchy` | None): A `TOMLHierarchy` instance or
            None. Defaults to None.
        key (str | None): A string corresponding to the key of data that
            is being inserted. Can also be None. Defaults to None.
    """
    _insert_into_toml_source(
        inserter=_PositionalInserter(
            toml_source=toml_source,
            hierarchy=hierarchy,
            key=key,
            insertion=insertion,
            position=position,
            by_attribute=True
        )
    )


def general_insert(
    toml_source: TOMLFieldSource,
    insertion: Any,
    hierarchy: Optional[TOMLHierarchy] = None,
    key: Optional[str] = None
) -> None:
    """
    Inserts an object that is tomlkit compatible based on a container
    position. A "container position" is an integer, indexed at 1,
    representing the position where the insertion object should be placed
    amongst all other types, including stylings (whitespace, comments),
    within a tomlkit type that supports insertion.
    
    The `toml_source` argument is the base tomlkit instance, and the
    `hierarchy` references the hierarchy relative to, and located within
    `toml_source` where the `insertion` argument will be placed.
    
    The `hierarchy` argument must exist within the `tomlkit` object,
    unless it is None. If this argument is passed in as None, then the
    insertion will occur at the top-level space of the `tomlkit` object.

    The `key` argument is the string key corresponding to the data that
    is being inserted. This should always be a string unless inserting in
    a array or array of tables. In those cases, a `key` should not be
    provided and will default to None.

    Args:
        toml_source (`TOMLFieldSource`): A `TOMLFieldSource` instance.
        insertion (Any): An instance of any type.
        hierarchy (`TOMLHierarchy` | None): A `TOMLHierarchy` instance or
            None. Defaults to None.
        key (str | None): A string corresponding to the key of data that
            is being inserted. Can also be None. Defaults to None.
    """
    _insert_into_toml_source(
        inserter=_GeneralInserter(
            toml_source=toml_source,
            hierarchy=hierarchy,
            key=key,
            insertion=insertion
        )
    )


class _BaseItemInserter(ABC):
    """
    A private base abstract class that is an abstract structure which provides
    tools to insert a `tomlkit.items.Item` object at a specific position within 
    a `tomlkit` type that supports insertion.
    """
    def __init__(self, item_to_insert: BodyContainerItemDecomposed, by_attribute: bool) -> None:
        self.item_inserted = False
        self.attribute, self.insertion = item_to_insert
        self.by_attribute = by_attribute

        self.attribute_position = self.container_position = 1

    @abstractmethod
    def add(self, item: items.Item, key: Optional[str] = None) -> None:
        """
        Abstract method to add a `tomlkit.items.Item` instance to a `tomlkit`
        structure.
        """
        pass

    def insert_attribute(self) -> None:
        """
        Inserts the relevant `items.Item` instance passed into the constructor
        to a `tomlkit` structure.
        """
        self.add(key=self.attribute, item=self.insertion)

    def insert_attribute_in_loop(self, position: int) -> None:
        """
        Runs within a for loop, and inserts the relevant `items.Item` instance
        passed into the constructor.

        Args:
            position (int): The current position when iterating through items in
                the body of a `BodyContainer` instance.
        """
        if (
            (self.attribute_position == position and self.by_attribute) or
            (self.container_position == position and not self.by_attribute)
        ):
            self.insert_attribute()
            self.item_inserted = True
            self.attribute_position += 1


class _DictLikeItemInserter(_BaseItemInserter):
    """
    A sub-class of `_BaseItemInserter` which provides tools to insert `tomlkit.items.Item`
    objects at specific positions within `tomlkit` dictionary-like types that support
    insertion.
    """
    def __init__(
        self,
        item_to_insert: Tuple[str, items.Item],
        container: Union[TOMLDocument, items.Table, items.InlineTable],
        by_attribute: bool = True
    ) -> None:
        super().__init__(item_to_insert=item_to_insert, by_attribute=by_attribute)
        self.container = container

    def add(self, item: items.Item, key: Optional[str] = None) -> None:
        """
        Adds a `tomlkit.items.Item` instance to a dict-like `tomlkit` type.
        
        Args:
            item (`items.Item`): A `tomlkit.items.Item` instance.
            key (str | None): A string representation of a key in a TOML file,
                can be a string or None.
        """
        if key is None:
            self.container.add(cast(Stylings, item))
        else:
            self.container.add(key, item)


class _ListLikeItemInserter(_BaseItemInserter):
    """
    A sub-class of `_BaseItemInserter` which provides tools to insert `tomlkit.items.Item`
    objects at specific positions within `tomlkit` list-like types that support insertion.
    """
    def __init__(
        self,
        item_to_insert: BodyContainerItemDecomposed,
        container: items.Array,
        by_attribute: bool = True
    ) -> None:
        super().__init__(item_to_insert=item_to_insert, by_attribute=by_attribute)
        self.container = container

    def add(self, item: items.Item, _: Optional[str] = None) -> None:
        """
        Adds a `tomlkit.items.Item` instance to a list-like `tomlkit` type.
        
        Args:
            item (`items.Item`): A `tomlkit.items.Item` instance.
        """
        self.container.append(item)


class _BaseInserter(ABC):
    """
    A private base abstract class that is an abstract structure which provides
    tools to run the entire insertion process to insert `tomlkit` types by
    attribute or container positions within `tomlkit` types that support insertion.
    """
    def __init__(
        self,
        toml_source: TOMLFieldSource,
        hierarchy: Optional[TOMLHierarchy],
        key: Optional[str],
        insertion: Any
    ) -> None:
        self.toml_source = toml_source
        self.key = key
        self.hierarchy_obj: Optional[Hierarchy] = None

        self.toml_item: items.Item = convert_to_tomlkit_item(value=insertion)

        if hierarchy is not None:
            self.hierarchy_obj = standardize_hierarchy(hierarchy=hierarchy)
        
    @abstractmethod
    def array_of_tables_insert(self, array_of_tables: items.AoT, table: items.Table) -> None:
        """
        An abstract method to insert an `tomlkit.items.Table` within an
        `tomlkit.items.AoT` instance.
        """
        pass

    @abstractmethod
    def insert(self, parent: BodyContainer) -> None:
        """
        An abstract method to insert an `tomlkit.items.Item` within a
        `tomlkit` type that is not a `tomlkit.items.AoT` instance.
        """
        pass

    def get_toml_source_insertion_object(self) -> ContainerLike:
        """
        Retrieve the point of insertion `tomlkit` type based on the `hierarchy`
        argument provided.

        There is logic to ensure that the `toml_source` is not nested within an
        array-of-tables, and that the parent is a valid `tomlkit` type that supports
        insertion.
        """
        parent: Union[TOMLFieldSource, items.Item]

        if self.hierarchy_obj is None:
            parent = self.toml_source
        else:
            retrieved_source = get_attribute_from_toml_source(
                hierarchy=self.hierarchy_obj, toml_source=self.toml_source
            )

            # Ensure the hierarchy does not map to a nested item within an array of
            # tables
            if (
                isinstance(retrieved_source, list) and
                not isinstance(retrieved_source, items.Item)
            ):
                raise TOMLInsertionError(
                    "Hierarchy maps to multiple items, insertion is not supported",
                    retrieved_source
                )
            
            parent = retrieved_source
        
        # Ensure that the hierarchy does not map to a type that does not support
        # insertion
        if not isinstance(
            parent,
            (
                TOMLDocument,
                items.Table,
                items.InlineTable,
                OutOfOrderTableProxy,
                items.Array,
                items.AoT,
            )
        ):
            raise TOMLInsertionError(
                "Hierarchy maps to a structure that does not support insertion",
                parent,
            )
        
        return parent


class _GeneralInserter(_BaseInserter):
    """
    A sub-class of `_BaseInserter` which provides tools to insert `tomlkit.items.Item`
    objects "generally", at the bottom of tomlkit types, that support insertion.
    """
    def array_of_tables_insert(
        self, array_of_tables: items.AoT, table: items.Table
    ) -> None:
        """
        Inserts an `tomlkit.items.Item` within an `tomlkit.items.AoT` instance
        for the "general" insert case.
        """
        array_of_tables.append(table)

    def insert(self, parent: BodyContainer) -> None:
        """
        Inserts an `tomlkit.items.Item` within a `tomlkit` type that is not
        a `tomlkit.items.AoT` instance.
        """
        if isinstance(parent, DICTIONARY_LIKE_TYPES):
            key = cast(str, self.key)
            parent[key] = self.toml_item
        else:
            parent.append(self.toml_item)


class _PositionalInserter(_BaseInserter):
    """
    A sub-class of `_BaseInserter` which provides tools to insert `tomlkit.items.Item`
    objects at specific positions within `tomlkit` types that support insertion.
    """
    def __init__(
        self,
        toml_source: TOMLFieldSource,
        hierarchy: Optional[TOMLHierarchy],
        key: Optional[str],
        insertion: Any,
        position: int,
        by_attribute: bool
    ) -> None:
        super().__init__(
            toml_source=toml_source,
            hierarchy=hierarchy,
            key=key,
            insertion=insertion
        )
        self.position = position
        self.by_attribute = by_attribute

    @property
    def body_item(self) -> BodyContainerItemDecomposed:
        """
        Returns a tuple containing the string key and `tomlkit.items.Item`
        of the item to be inserted
        """
        return (self.key, self.toml_item)

    def array_of_tables_insert(
        self, array_of_tables: items.AoT, table: items.Table
    ) -> None:
        """
        Inserts an `tomlkit.items.Item` within an `tomlkit.items.AoT` instance
        for the "positional" insert case.
        """
        array_of_tables.insert(self.position - 1, table)

    def insert(self, parent: BodyContainer) -> None:
        """
        Inserts an `tomlkit.items.Item` within a `tomlkit` type that is not
        a `tomlkit.items.AoT` instance.
        """
        item_to_insert: BodyContainerItemDecomposed = self.body_item
        toml_body_items = copy.deepcopy(get_container_body(toml_source=parent))
        _refresh_container(initial_container=parent)

        container: BodyContainerInOrder

        # If the parent of the insertion point is an out-of-order table,
        # then overwrite the container variable by creating a temporary
        # new items.Table instance.
        if isinstance(parent, OutOfOrderTableProxy):
            container = tomlkit.table()
        else:
            container = parent

        inserter: _BaseItemInserter

        # Conditional to create insert object for dict-like or list-like tomlkit types
        if isinstance(container, (TOMLDocument, items.Table, items.InlineTable)):
            inserter = _DictLikeItemInserter(
                item_to_insert=cast(Tuple[str, items.Item], item_to_insert),
                container=container,
                by_attribute=self.by_attribute
            )
        else:
            inserter = _ListLikeItemInserter(
                item_to_insert=item_to_insert,
                container=container,
                by_attribute=self.by_attribute
            )

        # For out-of-order tables, update the original parent container (which
        # has been cleared of its contents)
        if isinstance(parent, OutOfOrderTableProxy):
            parent.update(container)

        _insert_item_at_position_in_container(
            position=self.position,
            inserter=inserter,
            toml_body_items=toml_body_items
        )


def _insert_item_at_position_in_container(
    position: int, inserter: _BaseItemInserter, toml_body_items: BodyContainerItems
) -> None:
    """
    A private function which executes the insertion logic to place a `tomlkit.items.Item`
    object into a `BodyContainer` instance at a specific position.
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
            raise TypeError("Type is not a valid container-like structure")


def _insert_into_toml_source(inserter: _BaseInserter) -> None:
    """
    A private function which serves as the basis for all three insertion
    operations, `general_insert`, `attribute_insert`, and `container_insert`.
    """
    toml_source = inserter.get_toml_source_insertion_object()

    # For insertion into an array-of-tables, the item to be inserted must
    # only be an tomlkit.items.Table object
    if isinstance(toml_source, items.AoT):
        if not isinstance(inserter.toml_item, items.Table):
            raise TypeError(
                "Insertion at top level of an array of tables must be a table"
            )
        
        if inserter.key is not None:
            warnings.warn(
                "Not needed to pass 'key' when inserting into an array of tables",
                category=UserWarning
            )
        
        name: Optional[str] = None

        # Extract a correct string name from the items.AoT object or the
        # items.Table object being inserted
        if toml_source.name is not None:
            name = toml_source.name
        elif inserter.toml_item.name is not None:
            name = inserter.toml_item.name

        if inserter.key is None and name is None:
            raise KeyNotProvidedError(
                '`key` is requred or a `name` must exist in the array or table.'
            )

        if inserter.key != name and name is not None:
            inserter.key = name

        inserter.array_of_tables_insert(
            array_of_tables=toml_source, table=inserter.toml_item
        )

    # Otherwise the insertion is occuring into a dictionary-like object,
    # where the item to be inserted can be of any type, unless the source
    # is an inline table or array. If the source is an inline table, then
    # the type of the item should be one of the following:
    # - bool
    # - int
    # - float
    # - str
    # - datetime.datetime
    # - datetime.date
    # - datetime.time
    # - items.Array
    # - items.InlineTable
    else:
        if (
            isinstance(toml_source, (items.Array, items.InlineTable)) and
            not isinstance(inserter.toml_item, _VALID_ARRAY_OR_INLINE_TYPES)
        ):
            raise TypeError(
                "Cannot insert value of type "
                f"{type(inserter.toml_item).__name__} into an array."
            )
        
        # If the toml item inserted is an inline table or table or array, we can generate key?
        #####

        if isinstance(toml_source, DICTIONARY_LIKE_TYPES) and inserter.key is None:
            raise KeyNotProvidedError(
                '`key` is required for dictionary-like tomlkit types'
            )

        inserter.insert(parent=toml_source)