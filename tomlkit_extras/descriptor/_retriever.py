import re
from typing import (
    cast,
    Dict,
    List,
    Optional,
    Set
)

from tomlkit_extras.descriptor._store import DescriptorStore
from tomlkit_extras._typing import (
    StyleItem,
    TOMLHierarchy,
    TopLevelItem
)
from tomlkit_extras._hierarchy import (
    Hierarchy,
    standardize_hierarchy
)
from tomlkit_extras.descriptor._descriptors import (
    ArrayOfTablesDescriptor,
    ArrayOfTablesDescriptors,
    FieldDescriptor,
    StyleDescriptor,
    StylingDescriptors,
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
        stylings: StylingDescriptors
        
        is_comment = not re.match(_WHITESPACE_PATTERN, styling)

        if hierarchy is None:
            stylings = self._store.document._document_stylings # TODO: need to adjust
        else:
            hierarchy_obj = standardize_hierarchy(hierarchy=hierarchy)
            hierarchy_as_str: str = str(hierarchy_obj)

            if not self._store.tables.get(hierarchy=hierarchy_as_str):
                raise InvalidHierarchyError("Hierarchy does not exist in set of valid hierarchies")
            
            table_descriptor: TableDescriptor = self._store.tables.get(hierarchy=hierarchy_as_str)
            stylings = table_descriptor.stylings

        styling_space = stylings.comments if is_comment else stylings.whitespace
        if styling not in styling_space:
            raise InvalidStylingError("Styling does not exist in set of valid stylings")
        
        return [styling_descriptor for styling_descriptor in styling_space[styling]]
    
    def get_top_level_stylings(self, styling: StyleItem) -> List[StyleDescriptor]:
        """"""
        stylings: Dict[str, List[StyleDescriptor]]
        styling_descriptors: StylingDescriptors

        if self._top_level_hierarchy is None:
            styling_descriptors = self._store.document._document_stylings # TODO: need to adjust
        elif (
            self._top_level_type == 'table' and
            self._store.tables.contains(hierarchy=self._top_level_hierarchy)
        ):
            top_level_cast = cast(str, self._top_level_hierarchy)
            styling_descriptors = self._store.tables.get(hierarchy=top_level_cast).stylings
        else:
            styling_descriptors = StylingDescriptors(comments=dict(), whitespace=dict())

        if styling == 'comment':
            stylings = styling_descriptors.comments
        else:
            stylings = styling_descriptors.whitespace

        return [
            style_descriptor
            for stylings in stylings.values() for style_descriptor in stylings
        ]
    
    def get_table(self, hierarchy: TOMLHierarchy) -> TableDescriptor:
        """"""
        hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)   
        hierarchy_as_str = str(hierarchy_obj)

        if not self._store.tables.contains(hierarchy=hierarchy_as_str):
            raise InvalidHierarchyError("Hierarchy does not exist in set of valid hierarchies")

        table_descriptor: TableDescriptor = self._store.tables.get(hierarchy=hierarchy_as_str)
        return table_descriptor
    
    def get_field(self, hierarchy: TOMLHierarchy) -> FieldDescriptor:
        """"""
        field_descriptor: FieldDescriptor
        hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
        hierarchy_as_str = str(hierarchy_obj)

        if hierarchy_obj.hierarchy_depth == 1:
            if not self._store.document.contains(hierarchy=hierarchy_as_str):
                raise InvalidFieldError("Field does not exist in top-level document space")
            
            field_descriptor = self._store.document.get(hierarchy=hierarchy_as_str)
        else:
            longest_hierarchy: Optional[str] = hierarchy_obj.longest_ancestor_hierarchy(
                hierarchies=self._store.tables.hierarchies
            )

            if longest_hierarchy is None:
                raise InvalidHierarchyError("Hierarchy does not exist in set of valid hierarchies")

            table_descriptor: TableDescriptor = self._store.tables.get(hierarchy=longest_hierarchy)

            remaining_heirarchy = hierarchy_as_str.replace(longest_hierarchy, str())
            remaining_heirarchy = remaining_heirarchy.lstrip('.')
            
            if (
                not remaining_heirarchy or
                remaining_heirarchy not in table_descriptor.fields
            ):
                raise InvalidFieldError("Hierarchy does not map to an existing field")
            
            field_descriptor = table_descriptor.fields[remaining_heirarchy]

        return field_descriptor
    
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

        array_of_tables: ArrayOfTablesDescriptors = self._store.array_of_tables.get(
            hierarchy=longest_hierarchy
        )
        array_descriptors: List[ArrayOfTablesDescriptor] = array_of_tables.aots
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
        
        array_of_tables: ArrayOfTablesDescriptors = self._store.array_of_tables.get(
            hierarchy=longest_hierarchy
        )
        arrays: List[ArrayOfTablesDescriptor] = array_of_tables.aots

        table_descriptors: List[TableDescriptor] = []

        for array_of_table in arrays:            
            if hierarchy_as_str in array_of_table.tables:
                for table_descriptor in array_of_table.tables[hierarchy_as_str]:
                    table_descriptors.append(table_descriptor)

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

        array_of_tables: ArrayOfTablesDescriptors = self._store.array_of_tables.get(
            hierarchy=longest_hierarchy
        )
        arrays: List[ArrayOfTablesDescriptor] = array_of_tables.aots
        field_descriptors: List[FieldDescriptor] = []

        hierarchy_table = Hierarchy.parent_hierarchy(hierarchy=hierarchy_as_str)
        hierarchy_field = hierarchy_obj.attribute

        for array_of_table in arrays:
            if hierarchy_table in array_of_table.tables:
                for table in array_of_table.tables[hierarchy_table]:
                    if hierarchy_field in table.fields:
                        field_descriptor: FieldDescriptor = table.fields[hierarchy_field]
                        field_descriptors.append(field_descriptor)

        if not field_descriptors:
            raise InvalidFieldError("Hierarchy does not map to an existing field")

        return field_descriptors