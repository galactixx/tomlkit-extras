import itertools
from typing import (
    List,
    Optional
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
    AoTDescriptor,
    AoTDescriptors,
    FieldDescriptor,
    StyleDescriptor,
    StylingDescriptors,
    TableDescriptor
)
from tomlkit_extras._exceptions import (
    InvalidArrayOfTablesError,
    InvalidFieldError,
    InvalidHierarchyError,
    InvalidTableError
)

class DescriptorRetriever:
    """
    A class that houses get methods that retrieve certain TOML structures from a
    `DescriptorStore` instance. There are separate methods to retrieve fields and
    tables that appear within an array-of-tables and those that do not.

    Methods are provided to retrieve the following structures:
    - stylings (whitespaces and comments)
    - array-of-tables

    Not within an array-of-tables:
    - fields (including arrays)
    - tables (including inline tables)

    Within an array-of-tables:
    - fields (including arrays)
    - tables (including inline tables)
    """
    def __init__(
        self,
        store: DescriptorStore,
        top_level_type: TopLevelItem,
        top_level_hierarchy: Optional[str]
    ) -> None:
        self._store = store
        self._top_level_type = top_level_type
        self._top_level_hierarchy = top_level_hierarchy

    def get_stylings(
        self, styling: str, hierarchy: Optional[TOMLHierarchy]
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
        if hierarchy is None:
            return (
                self._store.document._document_stylings
                .get_styling(styling=styling)
            )
        else:
            hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
            hierarchy_as_str = str(hierarchy_obj)

            if self._store.tables.contains(hierarchy=str(hierarchy_obj)):
                return (
                    self._store.tables
                    .get(hierarchy=hierarchy_as_str)
                    .stylings
                    .get_styling(styling=styling)
                )
            else:
                table_descriptors = self._get_table_descriptors_from_aot(
                    hierarchy_obj=hierarchy_obj,
                    table_hierarchy=hierarchy_as_str
                )

                stylings = [
                    table.stylings.get_styling(styling=styling)
                    for table in table_descriptors
                ]

                return list(itertools.chain.from_iterable(stylings))
    
    def get_top_level_stylings(self, styling: Optional[StyleItem]) -> List[StyleDescriptor]:
        """
        Retrieves all stylings (comments or whitespace) that occur at the
        top-level of the TOML source.

        Args:
            styling (`StyleItem` | None): A literal that identifies the type of
                styling to retrieve. Can be either "whitespace" or "comment".
                Defaults to None.

        Returns:
            List[`StyleDescriptor`]: A list of `StyleDescriptor` instances.
        """
        descriptors: StylingDescriptors

        if (
            self._top_level_type == 'table' and
            self._top_level_hierarchy is not None and
            self._store.tables.contains(hierarchy=self._top_level_hierarchy)
        ):
            descriptors = (
                self._store
                .tables
                .get(hierarchy=self._top_level_hierarchy)
                .stylings
            )
        elif self._top_level_hierarchy is None:
            descriptors = self._store.document._document_stylings
        else:
            descriptors = StylingDescriptors(comments=dict(), whitespace=dict())

        return descriptors.get_stylings(styling=styling)
    
    def get_table(self, hierarchy: TOMLHierarchy) -> TableDescriptor:
        """
        Retrieves a table represented by a `TableDescriptor` object which
        corresponds to a specific hierarchy.
        
        Args:
            hierarchy (`TOMLHierarchy`) A `TOMLHierarchy` instance.
        
        Returns:
            `TableDescriptor`: A `TableDescriptor` instance.
        """
        hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)   
        hierarchy_as_str = str(hierarchy_obj)

        if not self._store.tables.contains(hierarchy=hierarchy_as_str):
            raise InvalidHierarchyError(
                "Hierarchy does not exist in set of valid hierarchies",
                hierarchy_obj,
                self._store.tables.hierarchies
            )

        return self._store.tables.get(hierarchy=hierarchy_as_str)
    
    def get_field(self, hierarchy: TOMLHierarchy) -> FieldDescriptor:
        """
        Retrieves a field represented by a `FieldDescriptor` object which
        corresponds to a specific hierarchy.
        
        Args:
            hierarchy (`TOMLHierarchy`) A `TOMLHierarchy` instance.
        
        Returns:
            `FieldDescriptor`: A `FieldDescriptor` instance.
        """
        field_descriptor: FieldDescriptor
        hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
        hierarchy_as_str = str(hierarchy_obj)

        if hierarchy_obj.depth == 1:
            if not self._store.document.contains(hierarchy=hierarchy_as_str):
                raise InvalidFieldError(
                    "Field does not exist in top-level document space",
                    hierarchy_obj,
                    self._store.document.fields
                )
            
            field_descriptor = self._store.document.get(hierarchy=hierarchy_as_str)
        else:
            # Take the hierarchy passed in and split it up into two parts. The
            # first part being the expected table hierarchy, and the second
            # the field name
            table_hierarchy = Hierarchy.parent_hierarchy(hierarchy=hierarchy_as_str)
            field = hierarchy_obj.attribute

            if not self._store.tables.contains(hierarchy=table_hierarchy):
                raise InvalidHierarchyError(
                    "Hierarchy does not exist in set of valid hierarchies",
                    hierarchy_obj,
                    self._store.tables.hierarchies
                )  
            
            # Retrieve the TableDescriptor instance from the table store
            table_descriptor = self._store.tables.get(hierarchy=table_hierarchy)

            # The field part of the hierarchy may have been passed incorrectly,
            # so there is a check below to ensure that it does exist
            if field not in table_descriptor.fields:
                raise InvalidFieldError(
                    "Hierarchy does not map to an existing field",
                    hierarchy_obj,
                    set(table_descriptor.fields.keys())
                )
            
            # Retrieve the FieldDescriptor instance from the TableDescriptor 
            field_descriptor = table_descriptor.fields[field]

        return field_descriptor
    
    def get_aot(self, hierarchy: TOMLHierarchy) -> List[AoTDescriptor]:
        """
        Retrieves all array-of-tables, where each array is represented
        by a `AoTDescriptor` object, that correspond to a specific hierarchy.

        Args:
            hierarchy (`TOMLHierarchy`) A `TOMLHierarchy` instance.
        
        Returns:
            List[`AoTDescriptor`]: A list of `AoTDescriptor` instances.
        """
        hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
        hierarchy_as_str = str(hierarchy_obj)

        if not self._store.array_of_tables.contains(hierarchy=hierarchy_as_str):
            raise InvalidArrayOfTablesError(
                "Hierarchy does not map to an existing array of tables",
                hierarchy_obj,
                self._store.array_of_tables.hierarchies
            )

        array_of_tables: AoTDescriptors = self._store.array_of_tables.get(
            hierarchy=hierarchy_as_str
        )
        return array_of_tables.aots
    
    def _get_table_descriptors_from_aot(
        self, hierarchy_obj: Hierarchy, table_hierarchy: str
    ) -> List[TableDescriptor]:
        """
        Private method that stores logic to get all `TableDescriptor` instances
        associated with a hierarchy that is located within an array-of-tables.
        """
        # There is a need to identify the part of the hierarchy that
        # corresponds to the array-of-tables
        longest_hierarchy = hierarchy_obj.longest_ancestor_hierarchy(
            hierarchies=self._store.array_of_tables.hierarchies
        )

        if longest_hierarchy is None:
            raise InvalidHierarchyError(
                "Hierarchy does not exist in set of valid hierarchies",
                hierarchy_obj,
                self._store.array_of_tables.hierarchies
            )
        
        # Grab all AoTDescriptor instances from the retrieved array
        array_of_tables: AoTDescriptors = self._store.array_of_tables.get(
            hierarchy=longest_hierarchy
        )
        arrays: List[AoTDescriptor] = array_of_tables.aots

        table_descriptors: List[List[TableDescriptor]] = [
            array.tables[table_hierarchy]
            for array in arrays if table_hierarchy in array.tables
        ]
        
        # In the event that no tables were found with the matching hierarchy
        if not table_descriptors:
            raise InvalidTableError(
                "Hierarchy does not map to an existing table within an array",
                hierarchy_obj,
                set(table for array in arrays for table in array.tables.keys())
            )

        return list(itertools.chain.from_iterable(table_descriptors))

    def get_table_from_aot(self, hierarchy: TOMLHierarchy) -> List[TableDescriptor]:
        """
        Retrieves all tables from an array-of-tables, where each table is represented
        by a `TableDescriptor` object, that correspond to a specific hierarchy.

        Args:
            hierarchy (`TOMLHierarchy`) A `TOMLHierarchy` instance.
        
        Returns:
            List[`TableDescriptor`]: A list of `TableDescriptor` instances.
        """
        hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
        
        table_descriptors: List[TableDescriptor] = self._get_table_descriptors_from_aot(
            hierarchy_obj=hierarchy_obj, table_hierarchy=str(hierarchy_obj)
        )

        return table_descriptors
    
    def get_field_from_aot(self, hierarchy: TOMLHierarchy) -> List[FieldDescriptor]:
        """
        Retrieves all fields from an array-of-tables, where each field is represented
        by a `FieldDescriptor` object, that correspond to a specific hierarchy.
        
        Args:
            hierarchy (`TOMLHierarchy`) A `TOMLHierarchy` instance.
        
        Returns:
            List[`FieldDescriptor`]: A list of `FieldDescriptor` instances.
        """
        hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)

        # Take the hierarchy passed in and split it up into two parts. The
        # first part being the expected table hierarchy, and the second
        # the field name
        table_hierarchy = Hierarchy.parent_hierarchy(hierarchy=str(hierarchy_obj))
        field = hierarchy_obj.attribute

        table_descriptors: List[TableDescriptor] = self._get_table_descriptors_from_aot(
            hierarchy_obj=hierarchy_obj, table_hierarchy=table_hierarchy
        )

        field_descriptors: List[FieldDescriptor] = [
            table_descriptor.fields[field]
            for table_descriptor in table_descriptors
            if field in table_descriptor.fields
        ]

        # In the event that no fields were found with the matching hierarchy
        if not field_descriptors:
            raise InvalidFieldError(
                "Hierarchy does not map to an existing field within an array",
                hierarchy_obj,
                set(
                    itertools.chain.from_iterable(
                        set(descriptor.fields.keys()) for descriptor in table_descriptors
                    )
                )
            )

        return field_descriptors