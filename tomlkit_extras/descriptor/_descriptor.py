from __future__ import annotations
import copy
import re
from typing import (
    cast,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Union
)

from tomlkit.container import OutOfOrderTableProxy
from tomlkit import items, TOMLDocument

from tomlkit_extras.toml._out_of_order import fix_out_of_order_table
from tomlkit_extras._utils import decompose_body_item, get_container_body
from tomlkit_extras._typing import (
    ContainerBody,
    ContainerInOrder,
    DescriptorInput,
    ParentItem,
    StyleItem,
    Stylings,
    Table,
    TableItem,
    TOMLHierarchy,
    TopLevelItem
)
from tomlkit_extras._hierarchy import (
    Hierarchy, 
    standardize_hierarchy
)
from tomlkit_extras._exceptions import (
    InvalidArrayOfTablesError,
    InvalidFieldError,
    InvalidHierarchyError,
    InvalidStylingError,
    InvalidTableError
)
from tomlkit_extras.descriptor._descriptors import (
    ArrayOfTablesDescriptor,
    FieldDescriptor,
    StyleDescriptor,
    TableDescriptor
)
from tomlkit_extras.descriptor._types import (
    ArrayOfTables,
    ArrayOfTablesPosition,
    ContainerInfo,
    FieldInfo,
    FieldPosition,
    ItemPosition,
    StylingInfo,
    StylingPosition,
    StylingPositions,
    TableInfo,
    TablePosition,
    TOMLItemInfo,
    TOMLStatistics
)
from tomlkit_extras.descriptor._helpers import (
    find_child_tables,
    get_item_type
)
from tomlkit_extras.descriptor._create import (
    create_field_descriptor,
    create_style_descriptor,
    create_table_descriptor
)

_WHITESPACE_PATTERN = r'^[ \n\r]*$'

class TOMLDocumentDescriptor:
    """"""
    def __init__(
        self, toml_source: DescriptorInput, top_level_only: bool = False
    ):
        self.top_level_only = top_level_only
        self.top_level_type: TopLevelItem = cast(
            TopLevelItem, get_item_type(toml_item=toml_source)
        )
        
        self.top_level_hierarchy: Optional[str]

        self._current_line_number = 0

        # Structures for storing any attributes occurring in top-level space
        self._document_lines: Dict[str, FieldPosition] = dict()
        self._document_stylings: StylingPositions = StylingPositions(
            comments=dict(), whitespace=dict()
        )

        # Structure for storing any array of tables objects
        self._array_of_tables: Dict[str, ArrayOfTables] = dict()

        # Structure for storing any attributes occurring within at least one table
        self._attribute_lines: Dict[str, TablePosition] = dict()

        # Statistics on number of types within TOML source
        self._toml_statistics = TOMLStatistics()

        position = ItemPosition(attribute=1, container=1)
        if isinstance(toml_source, items.AoT):
            self.top_level_hierarchy = toml_source.name
            assert toml_source.name is not None
            self._generate_descriptor_from_array_of_tables(
                hierarchy=str(), array=toml_source, position=position
            )          
        else:
            if isinstance(toml_source, items.Table):
                self.top_level_hierarchy = toml_source.name
                update_key = toml_source.name
                assert update_key is not None
            else:
                self.top_level_hierarchy = None
                update_key = str()

            self._generate_descriptor(
                container=toml_source,
                container_info=TOMLItemInfo.from_parent_type(key=update_key, hierarchy=str(), toml_item=toml_source),
                position=position
            )

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

    def is_field_instance(self, hierarchy: TOMLHierarchy) -> bool:
        """"""
        return self._is_instance(
            hierarchy=hierarchy, get_methods=['get_field', 'get_field_from_array_of_tables']
        )

    def is_array_of_tables_instance(self, hierarchy: TOMLHierarchy) -> bool:
        """"""
        return self._is_instance(
            hierarchy=hierarchy, get_methods=['get_array_of_tables']
        )

    def is_table_instance(self, hierarchy: TOMLHierarchy) -> bool:
        """"""
        return self._is_instance(
            hierarchy=hierarchy, get_methods=['get_table', 'get_table_from_array_of_tables']
        )
    
    def get_field_from_array_of_tables(self, hierarchy: TOMLHierarchy) -> List[FieldDescriptor]:
        """"""
        hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
        hierarchy_as_str: str = str(hierarchy_obj)

        longest_hierarchy: Optional[str] = hierarchy_obj.longest_sub_hierarchy(
            hierarchies=set(self._array_of_tables.keys())
        )

        if longest_hierarchy is None:
            raise InvalidHierarchyError("Hierarchy does not exist in set of valid array hierarchies")

        if longest_hierarchy == hierarchy_as_str:
            raise InvalidFieldError("Hierarchy does not map to an existing field")

        array_of_tables: ArrayOfTables = self._array_of_tables[longest_hierarchy]
        arrays: List[ArrayOfTablesPosition] = array_of_tables.aots
        field_descriptors: List[FieldDescriptor] = []

        hierarchy_table = Hierarchy.parent_hierarchy(hierarchy=hierarchy_as_str)
        hierarchy_field = str(cast(Hierarchy, hierarchy_obj.diff(hierarchy=hierarchy_table)))

        for array_of_table in arrays:
            if hierarchy_table in array_of_table.tables:
                for table in array_of_table.tables[hierarchy_table]:
                    if hierarchy_field in table.fields:
                        field_position: FieldPosition = table.fields[hierarchy_field]
                        
                        field_descriptors.append(
                            create_field_descriptor(
                                field=hierarchy_field,
                                hierarchy=hierarchy_obj,
                                field_position=field_position,
                                parent_type=table.item_type,
                                from_aot=True
                            )
                        )

        if not field_descriptors:
            raise InvalidFieldError("Hierarchy does not map to an existing field")

        return field_descriptors

    def get_table_from_array_of_tables(self, hierarchy: TOMLHierarchy) -> List[TableDescriptor]:
        """"""
        hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
        hierarchy_as_str = str(hierarchy_obj)

        longest_hierarchy: Optional[str] = hierarchy_obj.longest_sub_hierarchy(
            hierarchies=set(self._array_of_tables.keys())
        )

        if longest_hierarchy is None:
            raise InvalidHierarchyError("Hierarchy does not exist in set of valid hierarchies")
        
        array_of_tables: ArrayOfTables = self._array_of_tables[longest_hierarchy]
        arrays: List[ArrayOfTablesPosition] = array_of_tables.aots

        table_descriptors: List[TableDescriptor] = []

        for array_of_table in arrays:
            tables_from_array_of_table = list(array_of_table.tables.keys())
            
            if hierarchy_as_str in array_of_table.tables:
                for table_position in array_of_table.tables[hierarchy_as_str]:
                    child_tables: Set[Hierarchy] = find_child_tables(
                        root_hierarchy=hierarchy_as_str, hierarchies=tables_from_array_of_table
                    )

                    table_descriptors.append(
                        create_table_descriptor(
                            hierarchy=hierarchy_obj,
                            table_position=table_position,
                            tables=child_tables,
                            from_aot=True
                        )
                    )

        if not table_descriptors:
            raise InvalidTableError("Hierarchy does not map to an existing table")

        return table_descriptors

    def get_array_of_tables(self, hierarchy: TOMLHierarchy) -> List[ArrayOfTablesDescriptor]:
        """"""
        array_hierarchies: Set[str] = set(self._array_of_tables.keys())
        hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
        hierarchy_as_str = str(hierarchy_obj)

        longest_hierarchy: Optional[str] = hierarchy_obj.longest_sub_hierarchy(
            hierarchies=array_hierarchies
        )

        if longest_hierarchy is None or hierarchy_as_str != longest_hierarchy:
            raise InvalidArrayOfTablesError(
                "Hierarchy does not map to an existing array of tables"
            )

        shortest_hierarchy: Optional[str] = hierarchy_obj.shortest_sub_hierarchy(
            hierarchies=array_hierarchies
        )
        from_aot = shortest_hierarchy is not None and shortest_hierarchy != longest_hierarchy

        array_of_tables: ArrayOfTables = self._array_of_tables[longest_hierarchy]
        arrays: List[ArrayOfTablesPosition] = array_of_tables.aots

        array_descriptors: List[ArrayOfTablesDescriptor] = []
        for array_of_table in arrays:
            table_descriptors: List[TableDescriptor] = []

            tables_from_array_of_table = list(array_of_table.tables.keys())

            for table_hierarchy, tables in array_of_table.tables.items():
                for table_position in tables:
                    child_tables: Set[Hierarchy] = find_child_tables(
                        root_hierarchy=table_hierarchy, hierarchies=tables_from_array_of_table
                    )

                    table_descriptor: TableDescriptor = create_table_descriptor(
                        hierarchy=Hierarchy.from_str_hierarchy(hierarchy=table_hierarchy),
                        table_position=table_position,
                        tables=child_tables,
                        from_aot=True
                    )
                    table_descriptors.append(table_descriptor)

            array_descriptors.append(
                ArrayOfTablesDescriptor(
                    parent_type=array_of_table.parent_type,
                    name=array_of_table.name,
                    hierarchy=hierarchy_obj,
                    line_no=array_of_table.line_no,
                    attribute_pos=array_of_table.position.attribute,
                    container_pos=array_of_table.position.container,
                    comment=None,
                    from_aot=from_aot,
                    item_type=array_of_table.item_type,
                    tables=table_descriptors
                )
            )

        return array_descriptors

    def get_field(self, hierarchy: TOMLHierarchy) -> FieldDescriptor:
        """"""
        field_position: FieldPosition
        hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
        hierarchy_as_str = str(hierarchy_obj)

        parent_type: Union[TopLevelItem, TableItem]

        if hierarchy_obj.hierarchy_depth == 1:
            if hierarchy_as_str not in self._document_lines:
                raise InvalidFieldError("Field does not exist in top-level document space")
            
            field_position = self._document_lines[hierarchy_as_str]
            parent_type = self.top_level_type
            field = hierarchy_as_str
        else:
            longest_hierarchy: Optional[str] = hierarchy_obj.longest_sub_hierarchy(
                hierarchies=set(self._attribute_lines.keys())
            )

            if longest_hierarchy is None:
                raise InvalidHierarchyError("Hierarchy does not exist in set of valid hierarchies")

            table_position: TablePosition = self._attribute_lines[longest_hierarchy]
            remaning_hierarchy: Optional[Hierarchy] = hierarchy_obj.diff(hierarchy=longest_hierarchy)

            if (
                remaning_hierarchy is None or
                str(remaning_hierarchy) not in table_position.fields
            ):
                raise InvalidFieldError("Hierarchy does not map to an existing field")
            
            field_position = table_position.fields[str(remaning_hierarchy)]
            parent_type = table_position.item_type
            field = str(remaning_hierarchy)

        return create_field_descriptor(
            field=field,
            hierarchy=hierarchy_obj,
            field_position=field_position,
            parent_type=parent_type,
            from_aot=False
        )

    def get_table(self, hierarchy: TOMLHierarchy) -> TableDescriptor:
        """"""
        hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)   
        hierarchy_as_str = str(hierarchy_obj)

        if hierarchy_as_str not in self._attribute_lines:
            raise InvalidHierarchyError("Hierarchy does not exist in set of valid hierarchies")

        table_position: TablePosition = self._attribute_lines[hierarchy_as_str]
        child_tables = find_child_tables(
            root_hierarchy=hierarchy_as_str, hierarchies=list(self._attribute_lines.keys())
        )

        return create_table_descriptor(
            hierarchy=hierarchy_obj, table_position=table_position, tables=child_tables, from_aot=False
        )
    
    def get_top_level_stylings(self, styling: StyleItem) -> List[StyleDescriptor]:
        """"""
        stylings: Dict[str, List[StylingPosition]]
        styling_positions: StylingPositions

        if self.top_level_type == 'document':
            styling_positions = self._document_stylings
        elif (
            self.top_level_type == 'table' and
            self.top_level_hierarchy in self._attribute_lines
        ):
            styling_positions = self._attribute_lines[cast(str, self.top_level_hierarchy)].styling
        else:
            styling_positions = StylingPositions(comments=dict(), whitespace=dict())

        if styling == 'comment':
            stylings = styling_positions.comments
        else:
            stylings = styling_positions.whitespace

        hierarchy = (
            Hierarchy.from_str_hierarchy(hierarchy=self.top_level_hierarchy)
            if self.top_level_hierarchy is not None else None
        )

        return [
            create_style_descriptor(
                styling_position=styling_position, hierarchy=hierarchy, parent_type=self.top_level_type
            )
            for stylings in stylings.values() for styling_position in stylings
        ]

    def get_styling(self, styling: str, hierarchy: Optional[TOMLHierarchy] = None) -> List[StyleDescriptor]:
        """"""
        hierarchy_obj: Optional[Hierarchy] = None
        stylings: StylingPositions
        parent_type: ParentItem
        
        is_comment = not re.match(_WHITESPACE_PATTERN, styling)

        if hierarchy is not None:
            hierarchy_obj = standardize_hierarchy(hierarchy=hierarchy)
            hierarchy_as_str: str = str(hierarchy_obj)

            if hierarchy_as_str not in self._attribute_lines:
                raise InvalidHierarchyError("Hierarchy does not exist in set of valid hierarchies")
            
            table_position: TablePosition = self._attribute_lines[hierarchy_as_str]
            parent_type = table_position.item_type
            stylings = table_position.styling
        else:
            parent_type = self.top_level_type
            stylings = self._document_stylings

        styling_space = stylings.comments if is_comment else stylings.whitespace
        if styling not in styling_space:
            raise InvalidStylingError("Styling does not exist in set of valid stylings")
        
        return [
            create_style_descriptor(
                styling_position=styling_position, hierarchy=hierarchy_obj, parent_type=parent_type
            )
            for styling_position in styling_space[styling]
        ]
    
    def _is_instance(self, hierarchy: TOMLHierarchy, get_methods: List[str]) -> bool:
        """"""
        for get_method in get_methods:
            try:
                _ = getattr(self, get_method)(hierarchy)
            except (
                InvalidArrayOfTablesError,
                InvalidFieldError,
                InvalidHierarchyError,
                InvalidTableError
            ):
                pass
            else:
                return True
        return False

    def _get_array_hierarchy(self, hierarchy: TOMLHierarchy) -> Optional[str]:
        """"""
        if isinstance(hierarchy, Hierarchy):
            hierarchy_obj = hierarchy
        else:
            hierarchy_obj = Hierarchy.from_str_hierarchy(hierarchy=hierarchy)
        
        return hierarchy_obj.longest_sub_hierarchy(
            hierarchies=set(self._array_of_tables.keys())
        )

    def _get_aot_table(self, hierarchy: str) -> TablePosition:
        """"""
        array_hierarchy = cast(str, self._get_array_hierarchy(hierarchy=hierarchy))
        array_of_tables = self._array_of_tables[array_hierarchy]

        return array_of_tables.get_array(hierarchy=hierarchy).get_table(hierarchy=hierarchy)

    def _update_styling(
        self, container: ContainerInfo, style: StylingInfo, position: ItemPosition, is_aot: bool
    ) -> None:
        """"""
        styling_positions: StylingPositions

        if isinstance(container.item, TOMLDocument):
            styling_positions = self._document_stylings
        elif is_aot:
            table_position: TablePosition = self._get_aot_table(hierarchy=style.info.hierarchy)
            if isinstance(container.item, (items.Table, items.InlineTable)):
                styling_positions = table_position.styling
            else:
                styling_positions = table_position.fields[container.info.key].styling
        elif isinstance(container.item, (items.Table, items.InlineTable)):
            styling_positions = self._attribute_lines[style.info.hierarchy].styling
        else:
            if container.info.hierarchy:
                styling_positions = self._attribute_lines[style.info.hierarchy].fields[container.info.key].styling
            else:
                styling_positions = self._document_lines[container.info.key].styling

        styling_positions.update_stylings(
            style=style, position=position, line_no=self._current_line_number
        )

    def _update_attribute(self, item: FieldInfo, position: ItemPosition) -> None:
        """"""
        self._attribute_lines[item.info.hierarchy].add_field(
            item=item, line_no=self._current_line_number, position=position
        )

    def _update_top_level_space(self, item: FieldInfo, position: ItemPosition) -> None:
        """"""
        self._document_lines[item.info.key] = FieldPosition.from_toml_item(
            item=item, line_no=self._current_line_number, position=position
        )

    def _update_array_of_tables(self, item: FieldInfo, position: ItemPosition) -> None:
        """"""
        array_hierarchy = cast(str, self._get_array_hierarchy(hierarchy=item.info.hierarchy))
        array_of_tables = self._array_of_tables[array_hierarchy]

        table = array_of_tables.get_array(hierarchy=item.info.hierarchy).get_table(hierarchy=item.info.hierarchy)
        table.add_field(item=item, line_no=self._current_line_number, position=position)

    def _add_table_to_attributes(self, hierarchy: str, position: ItemPosition, table: TableInfo) -> None:
        """"""
        table_position = TablePosition.from_table_item(
            line_no=self._current_line_number, position=position, table=table
        )
        self._attribute_lines.update({hierarchy: table_position})

    def _add_table_to_array_of_tables(self, hierarchy: str, position: ItemPosition, table: TableInfo) -> None:
        """"""
        array_hierarchy = cast(str, self._get_array_hierarchy(hierarchy=hierarchy))
        array_of_tables = self._array_of_tables[array_hierarchy]

        table_position = TablePosition.from_table_item(
            line_no=self._current_line_number, position=position, table=table
        )

        array_of_tables.get_array(hierarchy=hierarchy).update_tables(
            hierarchy=hierarchy, table_position=table_position
        )

    def _update_attribute_descriptor(self, item: FieldInfo, position: ItemPosition, is_aot: bool) -> None:
        """"""
        if not item.info.hierarchy:
            self._update_top_level_space(item=item, position=position)
        elif is_aot:
            self._update_array_of_tables(item=item, position=position)
        else:
            self._update_attribute(item=item, position=position)

    def _update_array_comment(self, array: items.Array, item_info: TOMLItemInfo, is_aot: bool) -> None:
        """"""
        field_position: FieldPosition
        if not item_info.hierarchy:
            field_position = self._document_lines[item_info.key]
        elif is_aot:
            field_position = self._get_aot_table(hierarchy=item_info.hierarchy).fields[item_info.key]
        else:
            field_position = self._attribute_lines[item_info.hierarchy].fields[item_info.key]

        field_position.update_comment(item=array, line_no=self._current_line_number)

    def _generate_descriptor_from_array_of_tables(
        self, hierarchy: str, array: items.AoT, position: ItemPosition, parent_type: Optional[ParentItem] = None
    ) -> None:
        """"""
        array_name = cast(str, array.name)
        array_of_tables = ArrayOfTablesPosition(
            item_type='array-of-tables',
            parent_type=parent_type,
            name=array_name,
            line_no=self._current_line_number,
            position=copy.copy(position), 
            tables=dict(),
            table_indices=dict()
        )
        if hierarchy not in self._array_of_tables:
            self._array_of_tables[hierarchy] = ArrayOfTables(aots=[array_of_tables], array_indices={hierarchy: 0})
        else:
            self._array_of_tables[hierarchy].update_arrays(hierarchy=hierarchy, array=array_of_tables)

        hierarchy_parent = Hierarchy.parent_hierarchy(hierarchy=hierarchy)

        for index, table in enumerate(array.body):
            table_position = index + 1
            self._toml_statistics.add_table(table=table)
            table_item_info = TOMLItemInfo.from_parent_type(
                key=array_name, hierarchy=hierarchy_parent, toml_item=table, parent_type='array-of-tables'
            )
  
            self._generate_descriptor(
                container=table,
                container_info=table_item_info,
                position=ItemPosition(attribute=table_position, container=table_position),
                is_aot=True
            )

    def _generate_descriptor(
        self, container: ContainerInOrder, container_info: TOMLItemInfo, position: ItemPosition, is_aot: bool = False
    ) -> None:
        """"""
        new_position = ItemPosition(attribute=1, container=1)

        # Determine the new hierarchy
        if isinstance(container, items.Array):
            new_hierarchy = container_info.hierarchy
        else:
            new_hierarchy = Hierarchy.create_hierarchy(hierarchy=container_info.hierarchy, update=container_info.key)

        # Add a new table to the data structures
        if (
            isinstance(container, items.InlineTable) or
            (isinstance(container, items.Table) and not container.is_super_table())
        ):
            table = TableInfo(info=container_info, item=container)
            if is_aot:
                self._add_table_to_array_of_tables(hierarchy=new_hierarchy, position=position, table=table)
            else:
                self._add_table_to_attributes(hierarchy=new_hierarchy, position=position, table=table)

        # Since an inline table is contained only on a single line, and thus,
        # on the same line as the table header, the line number is intialized to 0
        table_body_items: ContainerBody = get_container_body(toml_source=container)
        if (
            isinstance(container, TOMLDocument) or
            (isinstance(container, items.Table) and not container.is_super_table())
        ):
            self._current_line_number += 1

        # Iterate through each item appearing in the body of the table/arrays,
        # unpack each item and process accordingly
        for toml_body_item in table_body_items:
            item_key, toml_item = decompose_body_item(body_item=toml_body_item)
            toml_item_info = TOMLItemInfo.from_body_item(
                hierarchy=new_hierarchy, container_info=container_info, body_item=(item_key, toml_item)
            )
            if isinstance(toml_item, OutOfOrderTableProxy):
                toml_item = fix_out_of_order_table(table=toml_item)
                toml_item_info.item_type.item_type = 'table'

            # If an inline table or array is encountered, the function
            # is run recursively since both data types can contain styling
            if isinstance(toml_item, items.Array):
                self._update_attribute_descriptor(item=FieldInfo(item=toml_item, info=toml_item_info), position=new_position, is_aot=is_aot)
                self._generate_descriptor(container=toml_item, container_info=toml_item_info, position=new_position, is_aot=is_aot)
                self._update_array_comment(array=toml_item, item_info=toml_item_info, is_aot=is_aot)

                self._toml_statistics.add_array(item=toml_item)
                self._current_line_number += 1
                new_position.update_positions()
            elif isinstance(toml_item, items.InlineTable):
                self._generate_descriptor(container=toml_item, container_info=toml_item_info, position=new_position, is_aot=is_aot)

                self._toml_statistics.add_inline_table(table=toml_item)
                self._current_line_number += 1
                new_position.update_positions()
            # If one of the two styling elements are encountered, then the
            # memory address of the instance is generated as the key
            elif isinstance(toml_item, (items.Comment, items.Whitespace)):
                number_of_newlines = toml_item.as_string().count('\n')
                self._update_styling(
                    container=ContainerInfo(info=container_info, item=container),
                    style=StylingInfo(info=toml_item_info, item=toml_item),
                    position=new_position,
                    is_aot=is_aot
                )
                self._current_line_number += number_of_newlines

                self._toml_statistics.add_comment(item=toml_item)
                new_position.update_body_position()
            # If the item is an array of tables
            elif isinstance(toml_item, items.AoT) and not self.top_level_only:
                self._toml_statistics.add_aot()
                self._generate_descriptor_from_array_of_tables(
                    hierarchy=container_info.full_hierarchy,
                    array=toml_item,
                    parent_type=cast(ParentItem, container_info.item_type.item_type),
                    position=new_position
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

                self._generate_descriptor(container=toml_item, container_info=toml_item_info, position=new_position, is_aot=is_aot)
                new_position.update_positions()
            elif not isinstance(toml_item, (items.Table, items.AoT)):
                if not isinstance(container, items.Array):
                    self._update_attribute_descriptor(item=FieldInfo(item=toml_item, info=toml_item_info), position=new_position, is_aot=is_aot)
                    if not isinstance(container, items.InlineTable):
                        self._current_line_number += 1

                    self._toml_statistics.add_field(item=toml_item)
                new_position.update_positions()