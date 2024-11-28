from abc import ABC, abstractmethod
from typing import (
    Any,
    cast,
    Dict,
    Optional,
    Set
)

from tomlkit import items

from tomlkit_extras.descriptor._helpers import (
    item_is_table,
    LineCounter
)
from tomlkit_extras._hierarchy import Hierarchy
from tomlkit_extras._typing import (
    BodyContainerInOrder,
    Item,
    Stylings,
    Table,
    TOMLHierarchy
)
from tomlkit_extras.descriptor._types import (
    ItemPosition,
    ItemInfo
)
from tomlkit_extras.descriptor._descriptors import (
    AoTDescriptor,
    AoTDescriptors,
    FieldDescriptor,
    StylingDescriptors,
    TableDescriptor
)

class BaseStore(ABC):
    """
    A base abstract class providing a general structure for all TOML stores
    used by the `TOMLDocumentDescriptor` class. These include the
    `DocumentStore`, `ArrayOfTablesStore` and `TableStore`.
    """
    @abstractmethod
    def get(self, hierarchy: str) -> Any:
        """"""
        pass

    @abstractmethod
    def contains(self, hierarchy: str) -> bool:
        """"""
        pass

    @abstractmethod
    def update(self, item: items.Item, info: ItemInfo, position: ItemPosition) -> None:
        """"""
        pass

    @abstractmethod
    def get_stylings(self, style_info: ItemInfo) -> StylingDescriptors:
        """"""
        pass

    @abstractmethod
    def get_array(self, info: ItemInfo) -> FieldDescriptor:
        """"""
        pass


class BaseTableStore(BaseStore):
    """
    A base abstract class providing a additional structure for all TOML stores
    that store data included in tables. These stores include
    `ArrayOfTablesStore` and `TableStore`.
    """
    @property
    @abstractmethod
    def hierarchies(self) -> Set[str]:
        pass

    @abstractmethod
    def add_table(
        self, 
        hierarchy: str, 
        table: Table, 
        info: ItemInfo,
        position: ItemPosition
    ) -> None:
        pass


class DocumentStore(BaseStore):
    """
    A sub-class of `BaseStore` which stores any fields or stylings that are part
    of the top-level of a `tomlkit.TOMLDocument` instance. Additional basic
    functionality is included to retrieve information from the store.
    """
    def __init__(self, line_counter: LineCounter) -> None:
        self._line_counter = line_counter
        self._document_fields: Dict[str, FieldDescriptor] = dict()
        self._document_stylings: StylingDescriptors = StylingDescriptors(
            comments=dict(), whitespace=dict()
        )

    def get(self, hierarchy: str) -> FieldDescriptor:
        """
        Given an field name will return a `FieldDescriptor` instance corresponding
        to that field. These are fields that appear at the top-level of the document,
        thus they are not nested with larger structures like tables.

        Args:
            hierarchy (str): A TOML hierarchy corresponding to field.

        Returns:
            `FieldDescriptor`: A `FieldDescriptor` instance.
        """
        return self._document_fields[hierarchy]
    
    def contains(self, hierarchy: str) -> bool:
        """
        A boolean method that checks to see if field exists in all those processed.
        Returns True if the field exists False if it does not exists.

        Args:
            hierarchy (str): A TOML hierarchy corresponding to the name of a field.

        Returns:
            bool: A boolean indicating whether the field exists.
        """
        return hierarchy in self._document_fields

    def update(self, item: items.Item, info: ItemInfo, position: ItemPosition) -> None:
        """
        Adds a new field to the store of fields already processed. A new key-value
        pair is added to the dictionary, where the key is the string name of the field,
        and the value is a `FieldDescriptor` instance.

        Args:
            item (`tomlkit.items.Item`): A `tomlkit.items.Item` instance corresponding
                to a field appearing in a TOML file.
            info (`ItemInfo`): An `ItemInfo` instance with basic info on the field.
            position (`ItemPosition`): An `ItemPosition` with position info on the field.
        """
        self._document_fields[info.key] = FieldDescriptor._from_toml_item(
            item=item, info=info, line_no=self._line_counter.line_no, position=position
        )

    def get_stylings(self, style_info: ItemInfo) -> StylingDescriptors:
        """
        Returns all stylings associated with a specific field. Stylings are separated
        by whether its whitespace or comments.

        Args:
            style_info (`ItemInfo`): An `ItemInfo` instance with basic info on the styling.
        
        Returns:
            `StylingDescriptors`: A `StylingDescriptors` instance containing all
                stylings associated with a field.
        """
        if style_info.parent_type == 'document':
            styling_positions = self._document_stylings
        else:
            field = Hierarchy.parent_level(hierarchy=style_info.hierarchy)
            styling_positions = self._document_fields[field].stylings
        return styling_positions
    
    def get_array(self, info: ItemInfo) -> FieldDescriptor:
        """
        Retrievies an array field from the store, based on an `ItemInfo` instance.

        Args:
            info (`ItemInfo`): An `ItemInfo` instance with basic info on the field.

        Returns:
            `FieldDescriptor`: A `FieldDescriptor` instance.
        """
        return self._document_fields[info.key]


class ArrayOfTablesStore(BaseTableStore):
    """
    A sub-class of `BaseTableStore` which stores any fields, tables, or stylings
    that are included in arrays of tables appearing in a `tomlkit.TOMLDocument`
    instance. Additional basic functionality is included to retrieve information
    from the store.
    """
    def __init__(self, line_counter: LineCounter) -> None:
        self._line_counter = line_counter
        self._array_of_tables: Dict[str, AoTDescriptors] = dict()

    @property
    def hierarchies(self) -> Set[str]:
        """
        Returns a set of hierarchies corresponding to all array of tables that have
        been processed.
        """
        return set(self._array_of_tables.keys())

    def get(self, hierarchy: str) -> AoTDescriptors:
        """
        Given an array of tables hierarchy will return a `AoTDescriptors`
        instance corresponding to that array.

        Args:
            hierarchy (str): A TOML hierarchy corresponding to an array of tables.

        Returns:
            `AoTDescriptors`: An `AoTDescriptors` instance.
        """
        return self._array_of_tables[hierarchy]
    
    def contains(self, hierarchy: str) -> bool:
        """
        A boolean method that checks to see if an array of tables hierarchy exists
        in all those processed. Returns True if the hierarchy exists False if it
        does not exists.

        Args:
            hierarchy (str): A TOML hierarchy corresponding to an array of tables.

        Returns:
            bool: A boolean indicating whether the hierarchy exists.
        """
        return hierarchy in self._array_of_tables

    def append(self, hierarchy: str, array_of_tables: AoTDescriptor) -> None:
        """
        Updates the existing array of tables store based on a hierarchy.
        
        If the hierarchy has not already been encountered then a new key-value pair
        is created where the key is the string hierarchy and the value is an
        `AoTDescriptors` instance.

        If the hierarchy has already been encountered, then the existing value
        corresponding to a `AoTDescriptors` instance is updated.
        
        Args:
            hierarchy (str): A TOML hierarchy corresponding to an array of tables.
            array_of_tables (`AoTDescriptors`): An `AoTDescriptors`
                instance.
        """
        if not hierarchy in self._array_of_tables:
            self._array_of_tables[hierarchy] = AoTDescriptors(
                aots=[array_of_tables], array_indices={hierarchy: 0}
            )
        else:
            self._array_of_tables[hierarchy].update_arrays(
                hierarchy=hierarchy, array=array_of_tables
            )

    def get_array_hierarchy(self, hierarchy: TOMLHierarchy) -> Optional[str]:
        """
        Given a `TOMLHierarchy` instance representing a TOML hierarchy, will return
        the longest ancestor hierarchy that exists in the store. This effectively
        finds the newest array of tables ancestor of the given hierarchy.

        If a corresponding hierarchy was found, then a string is returned. Otherwise
        None is returned.

        Args:
            hierarchy (`TOMLHierarchy`): A `TOMLHierarchy` instance.

        Returns:
            str | None: Returns a string hierarchy if a match was found in the store,
                otherwise returns None.
        """
        if isinstance(hierarchy, Hierarchy):
            hierarchy_obj = hierarchy
        else:
            hierarchy_obj = Hierarchy.from_str_hierarchy(hierarchy=hierarchy)
        return hierarchy_obj.longest_ancestor_hierarchy(hierarchies=self.hierarchies)
    
    def get_aot_table(self, hierarchy: str) -> TableDescriptor:
        """
        Retrieves a table located in an array of tables. Given a string table hierarchy
        will return a `TableDescriptor` instance.
        
        Args:
            hierarchy (str): A TOML hierarchy corresponding to a table.

        Returns:
            `TableDescriptor`: A `TableDescriptor` instance.
        """
        array_hierarchy = cast(str, self.get_array_hierarchy(hierarchy=hierarchy))
        array_of_tables = self._array_of_tables[array_hierarchy]

        return array_of_tables.get_array(hierarchy=hierarchy)._get_table(hierarchy=hierarchy)

    def update(self, item: items.Item, info: ItemInfo, position: ItemPosition) -> None:
        """
        Adds a new field to the store of fields already processed. A new key-value
        pair is added to the dictionary, where the key is the string name of the field,
        and the value is a `FieldDescriptor` instance.

        Args:
            item (`tomlkit.items.Item`): A `tomlkit.items.Item` instance corresponding
                to a field appearing in a TOML file.
            info (`ItemInfo`): An `ItemInfo` instance with basic info on the field.
            position (`ItemPosition`): An `ItemPosition` with position info on the field.
        """
        array_hierarchy = cast(str, self.get_array_hierarchy(hierarchy=info.hierarchy))
        array_of_tables = self._array_of_tables[array_hierarchy]

        array = array_of_tables.get_array(hierarchy=info.hierarchy)
        table = array._get_table(hierarchy=info.hierarchy)
        table._add_field(
            item=item,
            info=info,
            line_no=self._line_counter.line_no,
            position=position
        )

    def add_table(
        self,
        hierarchy: str,
        table: Table,
        info: ItemInfo,
        position: ItemPosition
    ) -> None:
        """
        Adds a new table to the store of tables already processed. A new key-value
        pair is added to the dictionary, where the key is the string hierarchy of the table,
        and the value is a `TableDescriptor` instance.
        
        Args:
            hierarchy (str): A TOML hierarchy corresponding to a table.
            table (`Table`): A Table instance, being either a tomlkit.items.Table or
                tomlkit.items.InlineTable.
            info (`ItemInfo`): An `ItemInfo` instance with basic info on the table.
            position (`ItemPosition`): An `ItemPosition` with position info on the table.
        """
        array_hierarchy = cast(str, self.get_array_hierarchy(hierarchy=hierarchy))
        array_of_tables = self._array_of_tables[array_hierarchy]

        table_descriptor = TableDescriptor._from_table_item(
            table=table,
            info=info,
            position=position,
            line_no=self._line_counter.line_no
        )

        array = array_of_tables.get_array(hierarchy=hierarchy)
        array._update_tables(hierarchy=hierarchy, table_descriptor=table_descriptor)

    def get_stylings(self, style_info: ItemInfo) -> StylingDescriptors:
        """
        Returns all stylings associated with a specific table. Stylings are separated
        by whether its whitespace or comments.

        Args:
            style_info (`ItemInfo`): An `ItemInfo` instance with basic info on the styling.
        
        Returns:
            `StylingDescriptors`: A `StylingDescriptors` instance containing all
                stylings associated with a table.
        """
        table_descriptor: TableDescriptor = self.get_aot_table(hierarchy=style_info.hierarchy)
        if item_is_table(item_type=style_info.parent_type):
            styling_descriptors = table_descriptor.stylings
        else:
            field = Hierarchy.parent_level(hierarchy=style_info.hierarchy)
            styling_descriptors = table_descriptor.fields[field].stylings
        return styling_descriptors
    
    def get_array(self, info: ItemInfo) -> FieldDescriptor:
        """
        Retrievies an array field from the store, based on an `ItemInfo` instance.

        Args:
            info (`ItemInfo`): An `ItemInfo` instance with basic info on the field.

        Returns:
            `FieldDescriptor`: A `FieldDescriptor` instance.
        """
        return self.get_aot_table(hierarchy=info.hierarchy).fields[info.key]


class TableStore(BaseTableStore):
    """
    A sub-class of `BaseTableStore` which stores any fields or stylings that
    are included in tables appearing in a tomlkit.TOMLDocument instance, but
    not appearing within an array of tables. Additional basic functionality
    is included to retrieve information from the store.
    """
    def __init__(self, line_counter: LineCounter) -> None:
        self._line_counter = line_counter
        self._tables: Dict[str, TableDescriptor] = dict()

    @property
    def hierarchies(self) -> Set[str]:
        """
        Returns a set of hierarchies corresponding to all tables that do not appear
        in any array of tables structures.
        """
        return set(self._tables.keys())

    def get(self, hierarchy: str) -> TableDescriptor:
        """
        Given a table hierarchy will return a `TableDescriptor` instance
        corresponding to that table.

        Args:
            hierarchy (str): A TOML hierarchy corresponding to a table.

        Returns:
            `TableDescriptor`: A `TableDescriptor` instance.
        """
        return self._tables[hierarchy]
    
    def contains(self, hierarchy: str) -> bool:
        """
        A boolean method that checks to see if a table hierarchy exists in
        all tables processed. Returns True if the hierarchy exists False if it
        does not exists.

        Args:
            hierarchy (str): A TOML hierarchy corresponding to a table.

        Returns:
            bool: A boolean indicating whether the hierarchy exists.
        """
        return hierarchy in self._tables

    def update(self, item: items.Item, info: ItemInfo, position: ItemPosition) -> None:
        """
        Adds a new field to the store of fields already processed. A new key-value
        pair is added to the dictionary, where the key is the string name of the field,
        and the value is a `FieldDescriptor` instance.

        Args:
            item (`tomlkit.items.Item`): A `tomlkit.items.Item` instance corresponding
                to a field appearing in a TOML file.
            info (`ItemInfo`): An `ItemInfo` instance with basic info on the field.
            position (`ItemPosition`): An `ItemPosition` with position info on the field.
        """
        self._tables[info.hierarchy]._add_field(
            item=item,
            info=info,
            position=position,
            line_no=self._line_counter.line_no
        )

    def add_table(
        self,
        hierarchy: str,
        table: Table,
        info: ItemInfo,
        position: ItemPosition
    ) -> None:
        """
        Adds a new table to the store of tables already processed. A new key-value
        pair is added to the dictionary, where the key is the string hierarchy of the
        table, and the value is a `TableDescriptor` instance.
        
        Args:
            hierarchy (str): A TOML hierarchy corresponding to a table.
            table (`Table`): A Table instance, being either a tomlkit.items.Table or
                tomlkit.items.InlineTable.
            info (`ItemInfo`): An `ItemInfo` instance with basic info on the table.
            position (`ItemPosition`): An `ItemPosition` with position info on the table.
        """
        table_descriptor = TableDescriptor._from_table_item(
            table=table,
            info=info,
            position=position,
            line_no=self._line_counter.line_no
        )
        self._tables.update({hierarchy: table_descriptor})

    def get_stylings(self, style_info: ItemInfo) -> StylingDescriptors:
        """
        Returns all stylings associated with a specific table. Stylings are separated
        by whether its whitespace or comments.

        Args:
            style_info (`ItemInfo`): An `ItemInfo` instance with basic info on the styling.
        
        Returns:
            `StylingDescriptors`: A `StylingDescriptors` instance containing all
                stylings associated with a table.
        """
        if item_is_table(item_type=style_info.parent_type):
            styling_positions = self._tables[style_info.hierarchy].stylings
        else:
            field = Hierarchy.parent_level(hierarchy=style_info.hierarchy)
            hierarchy = Hierarchy.parent_hierarchy(hierarchy=style_info.hierarchy)
            styling_positions = self._tables[hierarchy].fields[field].stylings
        return styling_positions
    
    def get_array(self, info: ItemInfo) -> FieldDescriptor:
        """
        Retrievies an array field from the store, based on an `ItemInfo` instance.

        Args:
            info (`ItemInfo`): An `ItemInfo` instance with basic info on the field.

        Returns:
            `FieldDescriptor`: A `FieldDescriptor` instance.
        """
        return self._tables[info.hierarchy].fields[info.key]


class DescriptorStore:
    """
    A consolidated store which manages and maintains all three major stores,
    `DocumentStore`, `ArrayOfTablesStore`, and `TableStore`.

    Attributes:
        document (`DocumentStore`): A store for all fields and stylings appearing
            in the top-level space of the TOML file.
        array_of_tables (`ArrayOfTablesStore`): A store for all array of tables
            appearing within the TOML file.
        tables (`TableStore`): A store for all tables, not located in array of tables,
            appearing within the TOML file.
    """
    def __init__(self, line_counter: LineCounter) -> None:
        self._line_counter = line_counter
        
        # Structures for storing any attributes occurring in top-level space
        self.document = DocumentStore(line_counter=self._line_counter)

        # Structure for storing any array of tables objects
        self.array_of_tables = ArrayOfTablesStore(line_counter=self._line_counter)

        # Structure for storing any attributes occurring within at least one table
        self.tables = TableStore(line_counter=self._line_counter)

    def _store_choice(self, info: ItemInfo) -> BaseStore:
        """
        Private method which desides which of the three stores to update.
        """
        descriptor_store: BaseStore
        item_type: Item = info.item_type
        if (
            item_type == 'document' or
            not info.hierarchy and
            item_type in {'array', 'field', 'comment', 'whitespace'}
        ):
            descriptor_store = self.document
        elif info.from_aot:
            descriptor_store = self.array_of_tables
        else:
            descriptor_store = self.tables

        return descriptor_store

    def update_styling(
        self, style: Stylings, style_info: ItemInfo, position: ItemPosition
    ) -> None:
        """
        Adds a new styling, corresponding to a string comment or whitespace within
        a TOML file, to a store.
        """
        descriptor_store = self._store_choice(info=style_info)
        styling_positions = descriptor_store.get_stylings(style_info=style_info)
        styling_positions._update_stylings(
            style=style,
            info=style_info,
            position=position,
            line_no=self._line_counter.line_no
        )

    def update_field_descriptor(
        self, item: items.Item, info: ItemInfo, position: ItemPosition
    ) -> None:
        """
        Adds a new field, corresponding to a non-table key-value pair within a TOML
        file, to a store.
        """
        descriptor_store = self._store_choice(info=info)
        descriptor_store.update(item=item, info=info, position=position)

    def update_array_comment(self, array: items.Array, info: ItemInfo) -> None:
        """
        Adds a comment to an array field, corresponding to a non-table key-value pair
        within a TOML file, to a store.
        """
        descriptor_store = self._store_choice(info=info)
        field_position = descriptor_store.get_array(info=info)
        field_position._update_comment(item=array, line_no=self._line_counter.line_no)

    def update_table_descriptor(
        self,
        hierarchy: str,
        container: BodyContainerInOrder,
        container_info: ItemInfo,
        position: ItemPosition,
    ) -> None:
        """
        Adds a new table, corresponding to a table pair within a TOML file, to a
        store.
        """
        if (
            isinstance(container, items.InlineTable) or
            (isinstance(container, items.Table) and not container.is_super_table())
        ):
            descriptor_store: BaseTableStore
            if container_info.from_aot:
                descriptor_store = self.array_of_tables
            else:
                descriptor_store = self.tables

            descriptor_store.add_table(
                hierarchy=hierarchy, table=container, info=container_info, position=position
            )