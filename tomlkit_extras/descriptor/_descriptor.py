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

class TOMLDocumentDescriptor:
    """
    A class that iterates through, maps out, and collects all relevant information
    for all fields, tables and stylings appearing in a `DescriptorInput` instance. A
    `DescriptorInput` instance is a `tomlkit` type of either `tomlkit.TOMLDocument`,
    `tomlkit.items.Table`, `tomlkit.items.AoT`, or `tomlkit.items.Array`. 
    
    Parsing occurs within the constructor. Methods are provided to retrieve basic
    summary statistics about the TOML file, and to extract granular information
    about fields, tables, or stylings appearing at a specific hierarchy.
    
    Args:
        toml_source (`DescriptorInput`): A `tomlkit` type of either
            `tomlkit.TOMLDocument`, `tomlkit.items.Table`, `tomlkit.items.AoT`, or
            `tomlkit.items.Array`
        top_level_only (bool): A boolean value that indicates whether only the
            top-level space of the `DescriptorInput` structure should be parsed.
            Defaults to False.
    """
    def __init__(
        self, toml_source: DescriptorInput, top_level_only: bool = False
    ):
        if not isinstance(toml_source, DescriptorInput):
            raise TypeError(
                'Expected an instance of DescriptorInput, but got '
                f'{type(toml_source).__name__}'
            )

        self.top_level_only = top_level_only
        self.top_level_type: TopLevelItem = cast(
            TopLevelItem, get_item_type(toml_item=toml_source)
        )
        self.top_level_hierarchy: Optional[str] = (
            toml_source.name if isinstance(toml_source, (items.AoT, items.Table)) else None
        )

        # Tracker for number of lines in TOML
        self._line_counter = LineCounter()

        # Descriptor store and retriever
        self._store = DescriptorStore(line_counter=self._line_counter)
        self._retriever = DescriptorRetriever(
            store=self._store,
            top_level_type=self.top_level_type,
            top_level_hierarchy=self.top_level_hierarchy
        )

        # Statistics on number of types within TOML source
        self._toml_statistics = TOMLStatistics()

        if isinstance(toml_source, (items.Table, items.AoT)):
            update_key = toml_source.name
            assert (
                update_key is not None,
                'table or array-of-tables must have a string name'
            )
        else:
            update_key = str()

        container_info = ItemInfo.from_parent_type(
            key=update_key, hierarchy=str(), toml_item=toml_source
        )

        # Initialize the main functionality depending on whether the source
        # is an array-of-tables or not
        if isinstance(toml_source, items.AoT):
            self._generate_descriptor_from_aot(array=toml_source, info=container_info)
        else:
            self._generate_descriptor(container=toml_source, info=container_info)

        self._line_counter.reset_line_no()

    @property
    def number_of_tables(self) -> int:
        """
        Returns an integer representing the number of non-inline/non-super tables
        appearing in the TOML file.
        """
        return self._toml_statistics._number_of_tables

    @property
    def number_of_inline_tables(self) -> int:
        """
        Returns an integer representing the number of inline tables appearing in
        the TOML file.
        """
        return self._toml_statistics._number_of_inline_tables

    @property
    def number_of_aots(self) -> int:
        """
        Returns an integer representing the number of array-of-tables appearing
        in the TOML file.
        """
        return self._toml_statistics._number_of_aots
    
    @property
    def number_of_arrays(self) -> int:
        """
        Returns an integer representing the number of arrays appearing in the
        TOML file.
        """
        return self._toml_statistics._number_of_arrays

    @property
    def number_of_comments(self) -> int:
        """
        Returns an integer representing the number of comments appearing in the
        TOML file.
        """
        return self._toml_statistics._number_of_comments

    @property
    def number_of_fields(self) -> int:
        """
        Returns an integer representing the number of non-array fields appearing
        in the TOML file.
        """
        return self._toml_statistics._number_of_fields

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
    
    def get_top_level_stylings(self, styling: StyleItem) -> List[StyleDescriptor]:
        """
        Retrieves all stylings (comments or whitespace) that occur at the
        top-level of the TOML source.

        Args:
            styling (`StyleItem`): A literal that identifies the type of styling
                to retrieve. Can be either "whitespace" or "comment".

        Returns:
            List[`StyleDescriptor`]: A list of `StyleDescriptor` instances.
        """
        return self._retriever.get_top_level_stylings(styling=styling)

    def get_styling(
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
        return self._retriever.get_styling(styling=styling, hierarchy=hierarchy)

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

        # Add a new table to the data structures
        self._store.update_table_descriptor(
            hierarchy=new_hierarchy, container=container, container_info=info,
        )

        # Since an inline table is contained only on a single line, and thus,
        # on the same line as the table header, the line number is intialized to 0
        table_body_items: BodyContainerItems = get_container_body(toml_source=container)
        if (
            isinstance(container, TOMLDocument) or
            (isinstance(container, items.Table) and not container.is_super_table())
        ):
            self._line_counter.add_line()

        # Iterate through each item appearing in the body of the table/arrays,
        # unpack each item and process accordingly
        for toml_body_item in table_body_items:
            item_key, toml_item = decompose_body_item(body_item=toml_body_item)
            toml_item_info = ItemInfo.from_body_item(
                hierarchy=new_hierarchy, container_info=info, body_item=(item_key, toml_item)
            )
            toml_item_info.position = position

            # If the item is an out-of-order table, then fix and update the
            # item type attribute
            if isinstance(toml_item, OutOfOrderTableProxy):
                toml_item = fix_out_of_order_table(table=toml_item)
                toml_item_info.item_type = 'table'

            # If an inline table or array is encountered, the function
            # is run recursively since both data types can contain styling
            if isinstance(toml_item, items.Array):
                self._store.update_field_descriptor(item=toml_item, info=toml_item_info)
                self._generate_descriptor(container=toml_item, info=toml_item_info)
                self._store.update_array_comment(array=toml_item, info=toml_item_info)

                # Add array to summary TOML statistics
                self._toml_statistics.add_array(item=toml_item)

                # Add a single line to line counter and update both attribute
                # and container positions
                self._line_counter.add_line()
                toml_item_info.position.update_positions()
            elif isinstance(toml_item, items.InlineTable):
                self._generate_descriptor(container=toml_item, info=toml_item_info)

                # Add inline-table to summary TOML statistics
                self._toml_statistics.add_inline_table(table=toml_item)

                # Add a single line to line counter and update both attribute
                # and container positions
                self._line_counter.add_line()
                toml_item_info.position.update_positions()
            # If one of the two styling elements are encountered, then the
            # memory address of the instance is generated as the key
            elif isinstance(toml_item, (items.Comment, items.Whitespace)):
                number_of_newlines = toml_item.as_string().count('\n')
                self._store.update_styling(style=toml_item, style_info=toml_item_info)

                # Add comment to summary TOML statistics
                self._toml_statistics.add_comment(item=toml_item)

                # Add the number of new lines appearing in the styling to
                # the line counter and update only the container position
                self._line_counter.add_lines(lines=number_of_newlines)
                toml_item_info.position.update_body_position()
            # If the item is an array of tables
            elif isinstance(toml_item, items.AoT) and not self.top_level_only:
                self._toml_statistics.add_aot()
                self._generate_descriptor_from_aot(array=toml_item, info=toml_item_info)
                toml_item_info.position.update_positions()
            # If a item instance is encountered that links to a field
            # (i.e. not a table or a field  in an array), then the attribute
            # mapping is updated
            elif (
                isinstance(toml_item, items.Table) and
                not self.top_level_only
            ):
                self._toml_statistics.add_table(table=toml_item)

                self._generate_descriptor(container=toml_item, info=toml_item_info)
                toml_item_info.position.update_positions()
            elif not isinstance(toml_item, (items.Table, items.AoT)):
                if not isinstance(container, items.Array):
                    self._store.update_field_descriptor(item=toml_item, info=toml_item_info)
                    if not isinstance(container, items.InlineTable):
                        self._line_counter.add_line()

                    self._toml_statistics.add_field(item=toml_item)
                toml_item_info.position.update_positions()