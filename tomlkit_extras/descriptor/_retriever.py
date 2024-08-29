import re
from typing import (
    cast,
    Dict,
    List,
    Optional,
    Set,
    Union
)

from tomlkit_extras.descriptor._store import DescriptorStore
from tomlkit_extras.descriptor._types import (
    ArrayOfTables,
    ArrayOfTablesPosition,
    FieldPosition,
    StylingPosition,
    StylingPositions,
    TablePosition
)
from tomlkit_extras._typing import (
    ParentItem,
    StyleItem,
    TableItem,
    TOMLHierarchy,
    TopLevelItem
)
from tomlkit_extras._hierarchy import (
    Hierarchy,
    standardize_hierarchy
)
from tomlkit_extras.descriptor._helpers import (
    find_child_tables
)
from tomlkit_extras.descriptor._create import (
    create_field_descriptor,
    create_style_descriptor,
    create_table_descriptor
)
from tomlkit_extras.descriptor._descriptors import (
    ArrayOfTablesDescriptor,
    FieldDescriptor,
    StyleDescriptor,
    TableDescriptor
)
from tomlkit_extras._exceptions import (
    InvalidArrayOfTablesError,
    InvalidFieldError,
    InvalidHierarchyError,
    InvalidStylingError,
    InvalidTableError
)

_WHITESPACE_PATTERN = r'^[ \n\r]*$'

class DescriptorRetriever:
    """"""
    def __init__(
        self,
        store: DescriptorStore,
        top_level_type: TopLevelItem,
        top_level_hierarchy: Optional[str]
    ):
        self._store = store
        self._top_level_type = top_level_type
        self._top_level_hierarchy = top_level_hierarchy

    def get_styling(self, styling: str, hierarchy: Optional[TOMLHierarchy]) -> List[StyleDescriptor]:
        """"""
        hierarchy_obj: Optional[Hierarchy] = None
        stylings: StylingPositions
        parent_type: ParentItem
        
        is_comment = not re.match(_WHITESPACE_PATTERN, styling)

        if hierarchy is not None:
            hierarchy_obj = standardize_hierarchy(hierarchy=hierarchy)
            hierarchy_as_str: str = str(hierarchy_obj)

            if not self._store.tables.get(hierarchy=hierarchy_as_str):
                raise InvalidHierarchyError("Hierarchy does not exist in set of valid hierarchies")
            
            table_position: TablePosition = self._store.tables.get(hierarchy=hierarchy_as_str)
            parent_type = table_position.item_type
            stylings = table_position.styling
        else:
            parent_type = self._top_level_type
            stylings = self._store.document._document_stylings # TODO: need to adjust

        styling_space = stylings.comments if is_comment else stylings.whitespace
        if styling not in styling_space:
            raise InvalidStylingError("Styling does not exist in set of valid stylings")
        
        return [
            create_style_descriptor(
                styling_position=styling_position, hierarchy=hierarchy_obj, parent_type=parent_type
            )
            for styling_position in styling_space[styling]
        ]
    
    def get_top_level_stylings(self, styling: StyleItem) -> List[StyleDescriptor]:
        """"""
        stylings: Dict[str, List[StylingPosition]]
        styling_positions: StylingPositions

        if self._top_level_hierarchy is None:
            styling_positions = self._store.document._document_stylings # TODO: need to adjust
        elif (
            self._top_level_type == 'table' and
            self._store.tables.contains(hierarchy=self._top_level_hierarchy)
        ):
            top_level_cast = cast(str, self._top_level_hierarchy)
            styling_positions = self._store.tables.get(hierarchy=top_level_cast).styling
        else:
            styling_positions = StylingPositions(comments=dict(), whitespace=dict())

        if styling == 'comment':
            stylings = styling_positions.comments
        else:
            stylings = styling_positions.whitespace

        hierarchy = (
            Hierarchy.from_str_hierarchy(hierarchy=self._top_level_hierarchy)
            if self._top_level_hierarchy is not None else None
        )

        return [
            create_style_descriptor(
                styling_position=styling_position, hierarchy=hierarchy, parent_type=self._top_level_type
            )
            for stylings in stylings.values() for styling_position in stylings
        ]
    
    def get_table(self, hierarchy: TOMLHierarchy) -> TableDescriptor:
        """"""
        hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)   
        hierarchy_as_str = str(hierarchy_obj)

        if not self._store.tables.contains(hierarchy=hierarchy_as_str):
            raise InvalidHierarchyError("Hierarchy does not exist in set of valid hierarchies")

        table_position: TablePosition = self._store.tables.get(hierarchy=hierarchy_as_str)
        child_tables = find_child_tables(
            root_hierarchy=hierarchy_as_str, hierarchies=self._store.tables.hierarchies
        )

        return create_table_descriptor(
            hierarchy=hierarchy_obj,
            table_position=table_position,
            tables=child_tables,
            from_aot=False
        )
    
    def get_field(self, hierarchy: TOMLHierarchy) -> FieldDescriptor:
        """"""
        field_position: FieldPosition
        hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
        hierarchy_as_str = str(hierarchy_obj)

        parent_type: Union[TopLevelItem, TableItem]

        if hierarchy_obj.hierarchy_depth == 1:
            if not self._store.document.contains(hierarchy=hierarchy_as_str):
                raise InvalidFieldError("Field does not exist in top-level document space")
            
            parent_type = self._top_level_type
            field = hierarchy_as_str
            field_position = self._store.document.get(hierarchy=hierarchy_as_str)
        else:
            longest_hierarchy: Optional[str] = hierarchy_obj.longest_ancestor_hierarchy(
                hierarchies=self._store.tables.hierarchies
            )

            if longest_hierarchy is None:
                raise InvalidHierarchyError("Hierarchy does not exist in set of valid hierarchies")

            table_position: TablePosition = self._store.tables.get(hierarchy=longest_hierarchy)

            remaining_heirarchy = hierarchy_as_str.replace(longest_hierarchy, str())
            remaining_heirarchy = remaining_heirarchy.lstrip('.')
            
            if (
                not remaining_heirarchy or
                remaining_heirarchy not in table_position.fields
            ):
                raise InvalidFieldError("Hierarchy does not map to an existing field")
            
            parent_type = table_position.item_type
            field = remaining_heirarchy
            field_position = table_position.fields[remaining_heirarchy]

        return create_field_descriptor(
            field=field,
            hierarchy=hierarchy_obj,
            field_position=field_position,
            parent_type=parent_type,
            from_aot=False
        )
    
    def get_array_of_tables(self, hierarchy: TOMLHierarchy) -> List[ArrayOfTablesDescriptor]:
        """"""
        array_hierarchies: Set[str] = self._store.array_of_tables.hierarchies
        hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
        hierarchy_as_str = str(hierarchy_obj)

        longest_hierarchy: Optional[str] = hierarchy_obj.longest_ancestor_hierarchy(
            hierarchies=array_hierarchies
        )

        if longest_hierarchy is None or hierarchy_as_str != longest_hierarchy:
            raise InvalidArrayOfTablesError(
                "Hierarchy does not map to an existing array of tables"
            )

        shortest_hierarchy: Optional[str] = hierarchy_obj.shortest_ancestor_hierarchy(
            hierarchies=array_hierarchies
        )
        from_aot = shortest_hierarchy is not None and shortest_hierarchy != longest_hierarchy

        array_of_tables: ArrayOfTables = self._store.array_of_tables.get(hierarchy=longest_hierarchy)
        arrays: List[ArrayOfTablesPosition] = array_of_tables.aots

        array_descriptors: List[ArrayOfTablesDescriptor] = []
        for array_of_table in arrays:
            table_descriptors: List[TableDescriptor] = []

            tables_from_array_of_table = set(array_of_table.tables.keys())

            for table_hierarchy, tables in array_of_table.tables.items():
                for table_position in tables:
                    child_tables: Set[str] = find_child_tables(
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
    
    def get_table_from_array_of_tables(self, hierarchy: TOMLHierarchy) -> List[TableDescriptor]:
        """"""
        hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
        hierarchy_as_str = str(hierarchy_obj)

        longest_hierarchy: Optional[str] = hierarchy_obj.longest_ancestor_hierarchy(
            hierarchies=self._store.array_of_tables.hierarchies
        )

        if longest_hierarchy is None:
            raise InvalidHierarchyError("Hierarchy does not exist in set of valid hierarchies")
        
        array_of_tables: ArrayOfTables = self._store.array_of_tables.get(hierarchy=longest_hierarchy)
        arrays: List[ArrayOfTablesPosition] = array_of_tables.aots

        table_descriptors: List[TableDescriptor] = []

        for array_of_table in arrays:
            tables_from_array_of_table = set(array_of_table.tables.keys())
            
            if hierarchy_as_str in array_of_table.tables:
                for table_position in array_of_table.tables[hierarchy_as_str]:
                    child_tables: Set[str] = find_child_tables(
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
    
    def get_field_from_array_of_tables(self, hierarchy: TOMLHierarchy) -> List[FieldDescriptor]:
        """"""
        hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
        hierarchy_as_str: str = str(hierarchy_obj)

        longest_hierarchy: Optional[str] = hierarchy_obj.longest_ancestor_hierarchy(
            hierarchies=self._store.array_of_tables.hierarchies
        )

        if longest_hierarchy is None:
            raise InvalidHierarchyError("Hierarchy does not exist in set of valid array hierarchies")

        if longest_hierarchy == hierarchy_as_str:
            raise InvalidFieldError("Hierarchy does not map to an existing field")

        array_of_tables: ArrayOfTables = self._store.array_of_tables.get(hierarchy=longest_hierarchy)
        arrays: List[ArrayOfTablesPosition] = array_of_tables.aots
        field_descriptors: List[FieldDescriptor] = []

        hierarchy_table = Hierarchy.parent_hierarchy(hierarchy=hierarchy_as_str)
        hierarchy_field = hierarchy_obj.attribute

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