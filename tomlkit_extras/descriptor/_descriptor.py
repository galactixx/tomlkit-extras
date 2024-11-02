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
    ArrayOfTablesDescriptor,
    FieldDescriptor,
    StyleDescriptor,
    TableDescriptor
)
from tomlkit_extras.descriptor._types import (
    ItemPosition,
    ItemInfo,
    TOMLStatistics
)

class TOMLDocumentDescriptor:
    """"""
    def __init__(
        self, toml_source: DescriptorInput, top_level_only: bool = False
    ):
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

        position = ItemPosition(attribute=1, container=1)
        if isinstance(toml_source, (items.Table, items.AoT)):
            update_key = toml_source.name
            assert update_key is not None, 'table must have a string name'
        else:
            update_key = str()

        container_info = ItemInfo.from_parent_type(
            key=update_key, hierarchy=str(), toml_item=toml_source
        )

        if isinstance(toml_source, items.AoT):
            assert toml_source.name is not None, 'array of tables must have a string name'
            self._generate_descriptor_from_array_of_tables(
                array=toml_source, position=position, info=container_info
            )          
        else:
            self._generate_descriptor(
                container=toml_source, info=container_info, position=position
            )

        self._line_counter.reset_line_no()

    @property
    def number_of_tables(self) -> int:
        """"""
        return self._toml_statistics._number_of_tables

    @property
    def number_of_inline_tables(self) -> int:
        """"""
        return self._toml_statistics._number_of_inline_tables

    @property
    def number_of_aots(self) -> int:
        """"""
        return self._toml_statistics._number_of_aots
    
    @property
    def number_of_arrays(self) -> int:
        """"""
        return self._toml_statistics._number_of_arrays

    @property
    def number_of_comments(self) -> int:
        """"""
        return self._toml_statistics._number_of_comments

    @property
    def number_of_fields(self) -> int:
        """"""
        return self._toml_statistics._number_of_fields

    def get_field_from_array_of_tables(self, hierarchy: TOMLHierarchy) -> List[FieldDescriptor]:
        """"""
        return self._retriever.get_field_from_array_of_tables(hierarchy=hierarchy)

    def get_table_from_array_of_tables(self, hierarchy: TOMLHierarchy) -> List[TableDescriptor]:
        """"""
        return self._retriever.get_table_from_array_of_tables(hierarchy=hierarchy)

    def get_array_of_tables(self, hierarchy: TOMLHierarchy) -> List[ArrayOfTablesDescriptor]:
        """"""
        return self._retriever.get_array_of_tables(hierarchy=hierarchy)

    def get_field(self, hierarchy: TOMLHierarchy) -> FieldDescriptor:
        """"""
        return self._retriever.get_field(hierarchy=hierarchy)

    def get_table(self, hierarchy: TOMLHierarchy) -> TableDescriptor:
        """"""
        return self._retriever.get_table(hierarchy=hierarchy)
    
    def get_top_level_stylings(self, styling: StyleItem) -> List[StyleDescriptor]:
        """"""
        return self._retriever.get_top_level_stylings(styling=styling)

    def get_styling(self, styling: str, hierarchy: Optional[TOMLHierarchy] = None) -> List[StyleDescriptor]:
        """"""
        return self._retriever.get_styling(styling=styling, hierarchy=hierarchy)

    def _generate_descriptor_from_array_of_tables(
        self, array: items.AoT, position: ItemPosition, info: ItemInfo
    ) -> None:
        """"""
        array_name = cast(str, array.name)
        hierarchy = Hierarchy.create_hierarchy(hierarchy=info.hierarchy, attribute=array_name)
        array_of_tables = ArrayOfTablesDescriptor(
            line_no=self._line_counter.line_no,
            info=info,
            position=position
        )
        self._store.array_of_tables.append(hierarchy=hierarchy, array_of_tables=array_of_tables)

        for index, table in enumerate(array.body):
            table_position = index + 1
            self._toml_statistics.add_table(table=table)
            table_item_info = ItemInfo.from_parent_type(
                key=array_name,
                hierarchy=info.hierarchy,
                toml_item=table,
                parent_type='array-of-tables',
                from_aot=True
            )
  
            self._generate_descriptor(
                container=table,
                info=table_item_info,
                position=ItemPosition(attribute=table_position, container=table_position)
            )

    def _generate_descriptor(
        self, container: BodyContainerInOrder, info: ItemInfo, position: ItemPosition
    ) -> None:
        """"""
        # Determine the new position and hierarchy
        new_position = ItemPosition(attribute=1, container=1)
        new_hierarchy = info.full_hierarchy

        # Add a new table to the data structures
        self._store.update_table_descriptor(
            hierarchy=new_hierarchy,
            container=container,
            container_info=info,
            position=position
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
            if isinstance(toml_item, OutOfOrderTableProxy):
                toml_item = fix_out_of_order_table(table=toml_item)
                toml_item_info.item_type = 'table'

            # If an inline table or array is encountered, the function
            # is run recursively since both data types can contain styling
            if isinstance(toml_item, items.Array):
                self._store.update_field_descriptor(
                    item=toml_item, info=toml_item_info, position=new_position
                )
                self._generate_descriptor(
                    container=toml_item, info=toml_item_info, position=new_position
                )
                self._store.update_array_comment(array=toml_item, info=toml_item_info)

                self._toml_statistics.add_array(item=toml_item)
                self._line_counter.add_line()
                new_position.update_positions()
            elif isinstance(toml_item, items.InlineTable):
                self._generate_descriptor(
                    container=toml_item, info=toml_item_info, position=new_position
                )

                self._toml_statistics.add_inline_table(table=toml_item)
                self._line_counter.add_line()
                new_position.update_positions()
            # If one of the two styling elements are encountered, then the
            # memory address of the instance is generated as the key
            elif isinstance(toml_item, (items.Comment, items.Whitespace)):
                number_of_newlines = toml_item.as_string().count('\n')
                self._store.update_styling(
                    style=toml_item, style_info=toml_item_info, position=new_position
                )
                self._line_counter.add_lines(lines=number_of_newlines)

                self._toml_statistics.add_comment(item=toml_item)
                new_position.update_body_position()
            # If the item is an array of tables
            elif isinstance(toml_item, items.AoT) and not self.top_level_only:
                self._toml_statistics.add_aot()
                self._generate_descriptor_from_array_of_tables(
                    array=toml_item, position=new_position, info=toml_item_info
                )
                new_position.update_positions()
            # If a item instance is encountered that links to a field
            # (i.e. not a table or a field  in an array), then the attribute
            # mapping is updated
            elif (
                isinstance(toml_item, items.Table) and
                not self.top_level_only
            ):
                self._toml_statistics.add_table(table=toml_item)

                self._generate_descriptor(
                    container=toml_item, info=toml_item_info, position=new_position
                )
                new_position.update_positions()
            elif not isinstance(toml_item, (items.Table, items.AoT)):
                if not isinstance(container, items.Array):
                    self._store.update_field_descriptor(
                        item=toml_item, info=toml_item_info, position=new_position
                    )
                    if not isinstance(container, items.InlineTable):
                        self._line_counter.add_line()

                    self._toml_statistics.add_field(item=toml_item)
                new_position.update_positions()