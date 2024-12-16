from __future__ import annotations

from typing import (
    cast,
    List,
    Optional
)

from tomlkit.container import OutOfOrderTableProxy
from tomlkit import items, TOMLDocument

from tomlkit_extras.descriptor._helpers import get_item_type, LineCounter
from tomlkit_extras.descriptor._retriever import DescriptorRetriever
from tomlkit_extras.descriptor._store import DescriptorStore
from tomlkit_extras.toml._out_of_order import fix_out_of_order_table
from tomlkit_extras._utils import decompose_body_item, get_container_body
from tomlkit_extras._hierarchy import Hierarchy
from tomlkit_extras._typing import (
    BodyContainerInOrder,
    BodyContainerItems,
    DescriptorInput,
    StyleItem,
    Stylings,
    Table,
    TOMLHierarchy,
    TopLevelItem
)
from tomlkit_extras.descriptor._descriptors import (
    AoTDescriptor,
    FieldDescriptor,
    StyleDescriptor,
    TableDescriptor
)
from tomlkit_extras.descriptor._types import (
    ItemInfo,
    ItemPosition,
    TOMLStatistics
)

class _TOMLParser:
    """
    A private parser class that houses all logic to accurately recursively parse
    through various `tomlkit` types. These types include `tomlkit.items.Array`,
    `tomlkit.items.InlineTable`, `tomlkit.items.Comment`, `tomlkit.items.Whitespace`,
    `tomlkit.items.AoT`, and `tomlkit.items.Table` among others.
    """
    def __init__(
        self,
        line_counter: LineCounter,
        store: DescriptorStore,
        toml_statistics: TOMLStatistics,
        top_level_only: bool
    ) -> None:
        self._line_counter = line_counter
        self._store = store
        self._toml_statistics = toml_statistics

        self.top_level_only = top_level_only

    def _generate_descriptor_from_aot(self, array: items.AoT, info: ItemInfo) -> None:
        """
        Private method that parses all objects within a `tomlkit.items.AoT`
        instance.

        Initial pre-processing of the array-of-tables occurs, and then the main
        recursive method `_generate_descriptor` is called to continue parsing any
        nested structures.
        """
        array_name = cast(str, array.name)
        hierarchy = Hierarchy.create_hierarchy(
            hierarchy=info.hierarchy, attribute=array_name
        )

        # Generate an AoTDescriptor object to initialize mini-store for nested
        # structures
        array_of_tables = AoTDescriptor(
            line_no=self._line_counter.line_no, info=info
        )

        # Append the newly-created AoTDescriptor object to array-of-tables store
        self._store.array_of_tables.append(
            hierarchy=hierarchy, array_of_tables=array_of_tables
        )

        # Iterate through each table in the body of the array and run the
        # main recursive parsing method on the table
        for index, table in enumerate(array.body):
            self._toml_statistics.add_table(table=table)
            table_item_info = ItemInfo.from_parent_type(
                key=array_name,
                hierarchy=info.hierarchy,
                toml_item=table,
                parent_type='array-of-tables',
                from_aot=True
            )
  
            # Run the main recursive parsing method on the table
            table_item_info.position = ItemPosition(index + 1, index + 1)
            self._generate_descriptor(container=table, info=table_item_info)

    def _parse_array(self, toml_item: items.Array, info: ItemInfo) -> None:
        """Private method to parse through `items.Array` instances."""
        self._store.update_field_descriptor(item=toml_item, info=info)
        self._generate_descriptor(container=toml_item, info=info)
        self._store.update_array_comment(array=toml_item, info=info)

        # Add array to TOML summary statistics
        self._toml_statistics.add_array(item=toml_item)

        # Add a single line to line counter and update both attribute
        # and container positions
        self._line_counter.add_line()
        info.position.update_positions()

    def _parse_inline_table(self, toml_item: items.InlineTable, info: ItemInfo) -> None:
        """Private method to parse through `items.InlineTable` instances."""
        self._generate_descriptor(container=toml_item, info=info)

        # Add inline-table to TOML summary statistics
        self._toml_statistics.add_inline_table(table=toml_item)

        # Add a single line to line counter and update both attribute
        # and container positions
        self._line_counter.add_line()
        info.position.update_positions()

    def _parse_stylings(self, toml_item: Stylings, info: ItemInfo) -> None:
        """Private method to parse through `items.Whitespace`/`items.Comment` instances."""
        number_of_newlines = toml_item.as_string().count('\n')
        self._store.update_styling(style=toml_item, style_info=info)

        # Add comment to TOML summary statistics
        self._toml_statistics.add_comment(item=toml_item)

        # Add the number of new lines appearing in the styling to
        # the line counter and update only the container position
        self._line_counter.add_lines(lines=number_of_newlines)
        info.position.update_body_position()

    def _parse_array_of_tables(self, toml_item: items.AoT, info: ItemInfo) -> None:
        """Private method to parse through `items.AoT` instances."""
        self._generate_descriptor_from_aot(array=toml_item, info=info)

        # Add array to TOML summary statistics
        self._toml_statistics.add_aot()

        # Update both attribute and container positions
        info.position.update_positions()

    def _parse_table(self, toml_item: items.Table, info: ItemInfo) -> None:
        """Private method to parse through `items.Table` instances."""
        self._generate_descriptor(container=toml_item, info=info)

        # Add table to TOML summary statistics
        self._toml_statistics.add_table(table=toml_item)

        # Update boh attribute and container positions
        info.position.update_positions()

    def _parse_others(
        self,
        toml_item: items.Item,
        info: ItemInfo,
        container: BodyContainerInOrder
    ) -> None:
        """Private method to parse through other `items.Item` instances."""
        if not isinstance(container, items.Array):
            self._store.update_field_descriptor(item=toml_item, info=info)
            if not isinstance(container, items.InlineTable):
                self._line_counter.add_line()

            self._toml_statistics.add_field(item=toml_item)
        info.position.update_positions()

    def _generate_descriptor(self, container: BodyContainerInOrder, info: ItemInfo) -> None:
        """
        Private recursive method that traverses an entire `BodyContainerInOrder`
        instance, being a `tomlkit` type `tomlkit.TOMLDocument`, `tomlkit.items.Table`,
        `tomlkit.items.InlineTable`, or `tomlkit.items.Array`.
        
        During traversal, each field, table, array, and styling (comment and
        whitespace) is parsed and a custom/curated set of data points are collected
        for each item parsed.
        """
        position = ItemPosition.default_position()
        new_hierarchy = Hierarchy.create_hierarchy(
            hierarchy=info.hierarchy, attribute=info.key
        )
        is_non_super_table = (
            isinstance(container, items.Table) and not container.is_super_table()
        )

        # If an tomlkit.items.InlineTable or tomlkit.items.Table, then add
        # a new table to the table store
        if (
            isinstance(container, items.InlineTable) or
            is_non_super_table
        ):
            self._store.update_table_descriptor(
                hierarchy=new_hierarchy, table=cast(Table, container), table_info=info,
            )

        # Since an inline table is contained only on a single line, and thus
        # on the same line as the table header, only update the line counter
        # if parsing a tomlkit.TOMLDocument or tomlkit.items.Table instance
        table_body_items: BodyContainerItems = get_container_body(toml_source=container)
        if (
            isinstance(container, TOMLDocument) or
            is_non_super_table
        ):
            self._line_counter.add_line()

        # Iterate through each item appearing in the body of the tomlkit object
        for toml_body_item in table_body_items:
            item_key, toml_item = decompose_body_item(body_item=toml_body_item)
            toml_item_info = ItemInfo.from_body_item(
                hierarchy=new_hierarchy, container_info=info, body_item=(item_key, toml_item)
            )

            # Set the position property for the active item
            toml_item_info.position = position

            # If the item is an out-of-order table, then fix and update the
            # item type attribute
            if isinstance(toml_item, OutOfOrderTableProxy):
                toml_item = fix_out_of_order_table(table=toml_item)
                toml_item_info.item_type = 'table'

            # If an array is encountered, the function is run recursively since
            # an array can contain stylings and nested tomlkit.items.Item objects
            if isinstance(toml_item, items.Array):
                self._parse_array(toml_item=toml_item, info=toml_item_info)

            # If an inline table is parsed, the function is run recursively since
            # an inline table can contain nested tomlkit.items.Item objects
            elif isinstance(toml_item, items.InlineTable):
                self._parse_inline_table(toml_item=toml_item, info=toml_item_info)

            # If one of the two styling objects are encountered, then the
            # styling is added to the store. No recursive call as stylings
            # cannot contain nested tomlkit objects
            elif isinstance(toml_item, (items.Comment, items.Whitespace)):
                self._parse_stylings(toml_item=toml_item, info=toml_item_info)

            # For an array-of-tables, recursive call is made as arrays can
            # contain any tomlkit object nested within except a tomlkit.TOMLDocument
            elif isinstance(toml_item, items.AoT) and not self.top_level_only:
                self._parse_array_of_tables(toml_item=toml_item, info=toml_item_info)

            # For a non-inline table, make a recursive call
            elif (
                isinstance(toml_item, items.Table) and
                not self.top_level_only
            ):
                self._parse_table(toml_item=toml_item, info=toml_item_info)

            # Otherwise the object is a generic tomlkit.items.Item
            elif not isinstance(toml_item, (items.Table, items.AoT)):
                self._parse_others(
                    toml_item=toml_item, info=toml_item_info, container=container
                )


class TOMLDocumentDescriptor:
    """
    A class that iterates through, maps out, and collects all relevant
    information for all fields, tables and stylings appearing in a
    `DescriptorInput` instance. A `DescriptorInput` instance is a `tomlkit`
    type of either `tomlkit.TOMLDocument`, `tomlkit.items.Table`,
    `tomlkit.items.AoT`, or `tomlkit.items.Array`. 
    
    Parsing occurs within the constructor. Methods are provided to retrieve
    basic summary statistics about the TOML file, and to extract granular
    information about fields, tables, or stylings appearing at a specific
    hierarchy.

    All out-of-order tables appearing in the TOML file will automatically be
    fixed when parsing. Thus, the line numbers may be innacurate for these
    TOML files.
    
    Args:
        toml_source (`DescriptorInput`): A `tomlkit` type of either
            `tomlkit.TOMLDocument`, `tomlkit.items.Table`, `tomlkit.items.AoT`,
            or `tomlkit.items.Array`
        top_level_only (bool): A boolean value that indicates whether only the
            top-level space of the `DescriptorInput` structure should be parsed.
            Defaults to False.
    """
    def __init__(
        self, toml_source: DescriptorInput, top_level_only: bool = False
    ) -> None:
        if not isinstance(
            toml_source, (TOMLDocument, items.Table, items.AoT, items.Array)
        ):
            raise TypeError(
                'Expected an instance of DescriptorInput, but got '
                f'{type(toml_source).__name__}'
            )

        self.top_level_only = top_level_only
        self.top_level_type: TopLevelItem = cast(
            TopLevelItem, get_item_type(toml_item=toml_source)
        )
        self.top_level_hierarchy: Optional[str] = (
            toml_source.name
            if isinstance(toml_source, (items.AoT, items.Table)) else None
        )

        # Tracker for number of lines in TOML
        self._line_counter = LineCounter()

        # Statistics on number of types within TOML source
        self._toml_statistics = TOMLStatistics()

        # Descriptor store
        self._store = DescriptorStore(line_counter=self._line_counter)

        # TOML parser
        self._toml_parser = _TOMLParser(
            line_counter=self._line_counter,
            store=self._store,
            toml_statistics=self._toml_statistics,
            top_level_only=self.top_level_only
        )

        # Descriptor retriever
        self._retriever = DescriptorRetriever(
            store=self._store,
            top_level_type=self.top_level_type,
            top_level_hierarchy=self.top_level_hierarchy
        )

        if isinstance(toml_source, (items.Table, items.AoT)):
            update_key = toml_source.name
            assert update_key is not None, 'table or array-of-tables must have a string name'
        else:
            update_key = str()

        container_info = ItemInfo.from_parent_type(
            key=update_key, hierarchy=str(), toml_item=toml_source
        )

        # Initialize the main functionality depending on whether the source
        # is an array-of-tables or not
        if isinstance(toml_source, items.AoT):
            self._toml_parser._generate_descriptor_from_aot(
                array=toml_source, info=container_info
            )
        else:
            self._toml_parser._generate_descriptor(
                container=toml_source, info=container_info
            )

        self._line_counter.reset_line_no()

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}'
            f'(type={self.top_level_type!r}, hierarchy={self.top_level_hierarchy!r})'
        )

    @property
    def number_of_tables(self) -> int:
        """
        Returns an integer representing the number of non-inline/non-super tables
        appearing in the TOML file.
        """
        return self._toml_statistics.number_of_tables

    @property
    def number_of_inline_tables(self) -> int:
        """
        Returns an integer representing the number of inline tables appearing in
        the TOML file.
        """
        return self._toml_statistics.number_of_inline_tables

    @property
    def number_of_aots(self) -> int:
        """
        Returns an integer representing the number of array-of-tables appearing
        in the TOML file.
        """
        return self._toml_statistics.number_of_aots
    
    @property
    def number_of_arrays(self) -> int:
        """
        Returns an integer representing the number of arrays appearing in the
        TOML file.
        """
        return self._toml_statistics.number_of_arrays

    @property
    def number_of_comments(self) -> int:
        """
        Returns an integer representing the number of comments appearing in the
        TOML file.
        """
        return self._toml_statistics.number_of_comments

    @property
    def number_of_fields(self) -> int:
        """
        Returns an integer representing the number of non-array fields appearing
        in the TOML file.
        """
        return self._toml_statistics.number_of_fields

    def get_field_from_aot(self, hierarchy: TOMLHierarchy) -> List[FieldDescriptor]:
        """
        Retrieves all fields from an array-of-tables, where each field is represented
        by a `FieldDescriptor` object, that correspond to a specific hierarchy.
        
        Args:
            hierarchy (`TOMLHierarchy`) A `TOMLHierarchy` instance.
        
        Returns:
            List[`FieldDescriptor`]: A list of `FieldDescriptor` instances.
        """
        return self._retriever.get_field_from_aot(hierarchy=hierarchy)

    def get_table_from_aot(self, hierarchy: TOMLHierarchy) -> List[TableDescriptor]:
        """
        Retrieves all tables from an array-of-tables, where each table is represented
        by a `TableDescriptor` object, that correspond to a specific hierarchy.

        Args:
            hierarchy (`TOMLHierarchy`) A `TOMLHierarchy` instance.
        
        Returns:
            List[`TableDescriptor`]: A list of `TableDescriptor` instances.
        """
        return self._retriever.get_table_from_aot(hierarchy=hierarchy)

    def get_aot(self, hierarchy: TOMLHierarchy) -> List[AoTDescriptor]:
        """
        Retrieves all array-of-tables, where each array is represented
        by a `AoTDescriptor` object, that correspond to a specific hierarchy.

        Args:
            hierarchy (`TOMLHierarchy`) A `TOMLHierarchy` instance.
        
        Returns:
            List[`AoTDescriptor`]: A list of `AoTDescriptor` instances.
        """
        return self._retriever.get_aot(hierarchy=hierarchy)

    def get_field(self, hierarchy: TOMLHierarchy) -> FieldDescriptor:
        """
        Retrieves a field represented by a `FieldDescriptor` object which
        corresponds to a specific hierarchy.
        
        Args:
            hierarchy (`TOMLHierarchy`) A `TOMLHierarchy` instance.
        
        Returns:
            `FieldDescriptor`: A `FieldDescriptor` instance.
        """
        return self._retriever.get_field(hierarchy=hierarchy)

    def get_table(self, hierarchy: TOMLHierarchy) -> TableDescriptor:
        """
        Retrieves a table represented by a `TableDescriptor` object which
        corresponds to a specific hierarchy.
        
        Args:
            hierarchy (`TOMLHierarchy`) A `TOMLHierarchy` instance.
        
        Returns:
            `TableDescriptor`: A `TableDescriptor` instance.
        """
        return self._retriever.get_table(hierarchy=hierarchy)
    
    def get_top_level_stylings(self, styling: Optional[StyleItem] = None) -> List[StyleDescriptor]:
        """
        Retrieves all stylings (comments or whitespace) that occur at the
        top-level space of the TOML source.

        If "whitespace" is passed all whitespace stylings will be returned. If
        "comment" is passed all comment stylings will be returned. If it is None,
        then all stylings will be returned.

        Args:
            styling (`StyleItem` | None): A literal that identifies the type of
                styling to retrieve. Can be either "whitespace" or "comment". Is
                optional and defaults to None.

        Returns:
            List[`StyleDescriptor`]: A list of `StyleDescriptor` instances.
        """
        return self._retriever.get_top_level_stylings(styling=styling)

    def get_stylings(
        self, styling: str, hierarchy: Optional[TOMLHierarchy] = None
    ) -> List[StyleDescriptor]:
        """
        Retrieves all stylings corresponding to a specific string representation,
        where each styling is represented by a `StyleDescriptor` object. In
        addition, if the search should be narrowed, a `TOMLHierarchy` object
        can be passed.
        
        A styling can either be whitespace or comment.
        
        Args:
            styling (str): A string representation of a comment or whitespace.
            hierarchy (`TOMLHierarchy` | None) A `TOMLHierarchy` instance. Is
                optional and defaults to None.
        
        Returns:
            List[`StyleDescriptor`]: A list of `StyleDescriptor` instances.
        """
        return self._retriever.get_stylings(styling=styling, hierarchy=hierarchy)