from abc import ABC, abstractmethod
from typing import (
    Any,
    List,
    Optional,
    Set,
    Union
)

from tomlkit_extras._hierarchy import Hierarchy
from tomlkit_extras._typing import (
    BodyContainerItems,
    Retrieval,
    TOMLFieldSource
)
from tomlkit_extras._utils import (
    decompose_body_item,
    safe_unwrap
)

# ==============================================================================
# General Base Error Class for all Errors
# ==============================================================================

class BaseTOMLError(Exception):
    """
    Base error class for all errors thrown in `tomlkit_extras`.
    
    Attributes:
        message (str): The string error message.
    """
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return self.message

# ==============================================================================
# TOML Reading Errors
# ==============================================================================

class TOMLReadError(BaseTOMLError):
    """
    Base error class for those related to reading in TOML files.
    
    Inherits attributes from `BaseTOMLError`:
    - `message`
    """
    def __init__(self, message: str) -> None:
        super().__init__(message=message)


class TOMLDecodingError(TOMLReadError):
    """
    Decoding error occurring when loading a TOML configuration file.
    
    Inherits attributes from `BaseTOMLError`:
    - `message`
    """
    def __init__(self, message: str) -> None:
        super().__init__(message=message)


class TOMLConversionError(TOMLReadError):
    """
    General TOML conversion error when reading in TOML files.
    
    Inherits attributes from `BaseTOMLError`:
    - `message`
    """
    def __init__(self, message: str) -> None:
        super().__init__(message=message)

# ==============================================================================
# Invalid Hierarchy Errors
# ==============================================================================

class InvalidTOMLStructureError(ABC, BaseTOMLError):
    """
    Abstract error class for those related to querying a hierarchy from a 
    tomlkit structure.

    Inherits attributes from `BaseTOMLError`:
    - `message`

    Attributes:
        hierarchy (`Hierarchy`): A representation of the hierarchy passed
            in as an argument which does not exist.
    """
    def __init__(self, message: str, hierarchy: Hierarchy) -> None:
        super().__init__(message=message)
        self._hierarchy_obj = hierarchy

    @property
    def hierarchy(self) -> str:
        """Returns a string representation of the hierarchy that was invalid."""
        return str(self._hierarchy_obj)
    
    @property
    @abstractmethod
    def closest_hierarchy(self) -> Optional[str]:
        """Returns the longest ancestor hierarchy that exists in the TOML file."""
        pass


class InvalidHierarchyError(InvalidTOMLStructureError):
    """
    Error occurring when a hierarchy does not exist in set of expected
    hierarchies.

    Inherits attributes from `InvalidTOMLStructureError`:
    - `message`
    - `hierarchy`

    Attributes:
        hierarchies (Set[str]): All hierarchies appearing in the space of
            the TOML file that is being queried. For example, if retrieving
            from a field in the top-level document space, then the hierarchies
            would represent all existing fields in that space.
        closest_hierarchy (str | None): The longest ancestor hierarchy of
            the invalid hierarchy that exists in the TOML file
    """
    def __init__(
        self, message: str, hierarchy: Hierarchy, hierarchies: Set[str]
    ) -> None:
        super().__init__(message=message, hierarchy=hierarchy)
        self.hierarchies = hierarchies
    
    @property
    def closest_hierarchy(self) -> Optional[str]:
        """Returns the longest ancestor hierarchy that exists in the TOML file."""
        return self._hierarchy_obj.longest_ancestor_hierarchy(
            hierarchies=self.hierarchies
        )


class InvalidFieldError(InvalidTOMLStructureError):
    """
    Error occurring when a field does not exist in set of expected fields.

    Inherits attributes from `InvalidTOMLStructureError`:
    - `message`
    - `hierarchy`

    Attributes:
        field (str): The string field name, corresponding to the last level
            of the hierarchy.
        existing_fields (Set[str]): All fields that exist at the same level
            where the field was expected to be located.
        closest_hierarchy (str | None): The longest ancestor hierarchy of
            the invalid hierarchy that exists in the TOML file
    """
    def __init__(
        self, message: str, hierarchy: Hierarchy, fields: Set[str]
    ) -> None:
        super().__init__(message=message, hierarchy=hierarchy)
        self.existing_fields = fields
        self.field: str = self._hierarchy_obj.attribute

    @property
    def closest_hierarchy(self) -> str:
        """Returns the longest ancestor hierarchy that exists in the TOML file."""
        return self._hierarchy_obj.base_hierarchy_str


class InvalidTableError(InvalidTOMLStructureError):
    """
    Error occurring when a table does not exist in a set of expected tables.
    This is thrown only when attempting to retrieve a table that exists
    within an array-of-tables.

    Inherits attributes from `InvalidTOMLStructureError`:
    - `message`
    - `hierarchy`

    Attributes:
        table (str): The string table name, corresponding to the last level
            of the hierarchy.
        existing_tables (Set[str]): All hierarchies that correspond to tables
            existing within arrays-of-tables.
        closest_hierarchy (str | None): The longest ancestor hierarchy of
            the invalid hierarchy that exists in the TOML file
    """
    def __init__(
        self, message: str, hierarchy: Hierarchy, tables: Set[str]
    ) -> None:
        super().__init__(message=message, hierarchy=hierarchy)
        self.existing_tables = tables
        self.table: str = self._hierarchy_obj.attribute

    @property
    def closest_hierarchy(self) -> Optional[str]:
        """Returns the longest ancestor hierarchy that exists in the TOML file."""
        return self._hierarchy_obj.longest_ancestor_hierarchy(
            hierarchies=self.existing_tables
        )


class InvalidArrayOfTablesError(InvalidTOMLStructureError):
    """
    Error occurring when referencing an invalid array of tables.
    
    Inherits attributes from `InvalidTOMLStructureError`:
    - `message`
    - `hierarchy`

    Attributes:
        arrays (Set[str]): All hierarchies corresponding to existing
            arrays-of-tables in the TOML file.
        closest_hierarchy (str | None): The longest ancestor hierarchy of
            the invalid hierarchy that exists in the TOML file
    """
    def __init__(
        self, message: str, hierarchy: Hierarchy, arrays: Set[str]
    ) -> None:
        super().__init__(message=message, hierarchy=hierarchy)
        self.arrays = arrays

    @property
    def closest_hierarchy(self) -> Optional[str]:
        """Returns the longest ancestor hierarchy that exists in the TOML file."""
        return self._hierarchy_obj.longest_ancestor_hierarchy(
            hierarchies=self.arrays
        )

# ==============================================================================
# Invalid Hierarchy when Modifying Errors (when using TOML utility functions)
# ==============================================================================

class HierarchyModificationError(BaseTOMLError):
    """
    Base error class for those related to modification of a hierarchy in a 
    tomlkit structure. Error raised when using the TOML utility functions.

    Inherits attributes from `BaseTOMLError`:
    - `message`
    """
    def __init__(self, message: str) -> None:
        super().__init__(message=message)


class InvalidHierarchyDeletionError(HierarchyModificationError):
    """
    Error ocurring when a TOML hierarchy that is to be deleted does not exist.

    Inherits attributes from `HierarchyModificationError`:
    - `message`
    """
    def __init__(self, message: str) -> None:
        super().__init__(message=message)


class InvalidHierarchyUpdateError(HierarchyModificationError):
    """
    Error ocurring when a TOML hierarchy that is to be updated does not exist.

    Inherits attributes from `HierarchyModificationError`:
    - `message`
    """
    def __init__(self, message: str) -> None:
        super().__init__(message=message)


class InvalidHierarchyRetrievalError(HierarchyModificationError):
    """
    Error ocurring when an object from a TOML hierarchy that is to be retrieved
    does not exist.

    Inherits attributes from `HierarchyModificationError`:
    - `message`
    """
    def __init__(self, message: str) -> None:
        super().__init__(message=message)

# ==============================================================================
# Other TOML-related errors
# ==============================================================================

class NotContainerLikeError(BaseTOMLError):
    """
    Error occuring when an object that is expected to be a container-like
    structure, which can "contain" nested objects, is not.

    Inherits attributes from `BaseTOMLError`:
    - `message`
    """
    def __init__(self, message: str) -> None:
        super().__init__(message=message)


class TOMLInsertionError(BaseTOMLError):
    """
    Error occuring when attempting to insert into an object that does not
    support insertion.

    Inherits attributes from `BaseTOMLError`:
    - `message`
    
    Attributes:
        struct_type (Type[`Retrieval` | `TOMLFieldSource`]): The type of
            the object when the insertion attempt was made.
    """
    def __init__(
        self, message: str, structure: Union[Retrieval, TOMLFieldSource]
    ) -> None:
        super().__init__(message=message)
        self.struct_type = type(structure)


class InvalidStylingError(BaseTOMLError):
    """
    Error occurring when a styling does not exist in set of expected stylings.
    
    Inherits attributes from `BaseTOMLError`:
    - `message`

    Attributes:
        stylings (Set[str]): All the unique stylings that appear within the
            TOML structure. This is a set that is pre-filtered based on whether
            the query was a comment or whitespace-like string.
    """
    def __init__(self, message: str, stylings: Set[str]) -> None:
        super().__init__(message=message)
        self.stylings = stylings


class InvalidArrayItemError(BaseTOMLError):
    """
    Error occurring when an item expected to exist in an array, does not.
    
    Inherits attributes from `BaseTOMLError`:
    - `message`

    Attributes:
        array_items (List[Any]): A list of all values appearing in the
            TOML array object.
    """
    def __init__(self, message: str, body: BodyContainerItems) -> None:
        super().__init__(message=message)

        self.array_items: List[Any] = [
            safe_unwrap(structure=decompose_body_item(body_item=item)[1])
            for item in body
        ]