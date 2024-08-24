from __future__ import annotations
from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Set,
    Type
)

from tomlkit_extras._hierarchy import Hierarchy
from tomlkit_extras._typing import (
    FieldItem,
    ParentItem,
    StyleItem,
    TableItem
)

@dataclass(frozen=True)
class CommentDescriptor:
    """
    A dataclass which provides detail for a comment that is directly
    associated with a particular field or table.

    Args:
        comment (str): A string representing the comment.
        line_no (int): An integer line number where the comment is located.
    """
    comment: str
    line_no: int


@dataclass(frozen=True)
class Descriptor(object):
    """
    Base descriptor class, which provides no functionality, but a series
    of common attributes for all sub-classes, those being `TableDescriptor`,
    `ArrayOfTablesDescriptor`, and `FieldDescriptor`.
    
    Args:
        parent_type (`ParentItem` | None): A `ParentItem` instance, corresponding
            to a string literal representing the type of the parent of the
            structure. Can be None if there is no parent.
        name (str): The name of the attribute (field, table, or array of tables).
        hierarchy (`Hierarchy`): A `Hierarchy` instance representing the full
            hierarchy of the structure.
        line_no (int): An integer line number marking the beginning of the
            structure.
        attribute_pos (int): An integer position of the structure amongst all
            other key value pairs (fields, tables) within the parent.
        container_pos (int): An integer position of the structure amongst all
            other types, including stylings (whitespace, comments), within the
            parent.
        comment (`CommentDescriptor` | None): A `CommentDescriptor` instance,
            correspondng to the comment associated with the structure. Can
            be None if there is no comment.
        from_aot (bool): A boolean indicating whether the structure is nested
            within an array of tables.
    """
    parent_type: Optional[ParentItem]
    name: str
    hierarchy: Hierarchy
    line_no: int
    attribute_pos: int
    container_pos: int
    comment: Optional[CommentDescriptor]
    from_aot: bool


@dataclass(frozen=True)
class TableDescriptor(Descriptor):
    """
    A dataclass which provides detail on a table or inline table, a
    key-value pair that can contain nested key-value pairs.

    Inherits attributes from `Descriptor`:
    - parent_type
    - name
    - hierarchy
    - line_no
    - attribute_pos
    - container_pos
    - comment
    - from_aot

    Args:
        item_type (`TableItem`): A `TableItem` instance, corresponding to
            a string literal representing the type of the table, that
            being either 'table' or 'inline-table'.
        fields (Dict[str, `FieldDescriptor`]): A dictionary which has
            key-value pairs each being a field contained in the table. The
            keys are strings representing names of fields (not tables) and
            the corresponding values are `FieldDescriptor` instances.
        child_tables (Set[str] | None): A set of string hierarchies where
            each hierarchy represents a child table. Can be None if there
            are no child tables.
    """
    item_type: TableItem
    fields: Dict[str, FieldDescriptor]
    child_tables: Optional[Set[str]]


@dataclass(frozen=True)
class ArrayOfTablesDescriptor(Descriptor):
    """
    A dataclass which provides detail on an array of tables, a list of
    tables.

    Inherits attributes from `Descriptor`:
    - parent_type
    - name
    - hierarchy
    - line_no
    - attribute_pos
    - container_pos
    - comment
    - from_aot

    Args:
        item_type (Literal['array-of-tables']): A string literal
            being 'array-of-tables'.
        tables (List[`TableDescriptor`]): A list of `TableDescriptor`
            instances where each one represents a table within the
            array of tables.
    """
    item_type: Literal['array-of-tables']
    tables: List[TableDescriptor]


@dataclass(frozen=True)
class FieldDescriptor(Descriptor):
    """
    A dataclass which provides detail on a field, a key-value pair
    that cannot contain nested key-value pairs.

    Inherits attributes from `Descriptor`:
    - parent_type
    - name
    - hierarchy
    - line_no
    - attribute_pos
    - container_pos
    - comment
    - from_aot

    Args:
        item_type (`FieldItem`): A `FieldItem` instance, corresponding
            to a string literal being either 'field' or 'array'.
        value (Any): The value of the field.
    """
    item_type: FieldItem
    value: Any

    @property
    def value_type(self) -> Type[Any]:
        """"""
        return type(self.value)


@dataclass(frozen=True)
class StyleDescriptor:
    """
    A dataclass which provides detail on a specific styling appearing
    in a tomlkit type instance.

    A styling can either be a comment, represented in tomlkit as a
    tomlkit.items.Comment instance, or a whitespace, represented as a
    tomlkit.items.Whitespace instance.

    These are comments or whitespaces that are not directly associated with
    a field or table, but are contained within tomlkit structures like tables. 

    Args:
        item_type (`StyleItem`): A `StyleItem` instance, corresponding to a
            string literal representing the type of the styling, being
            either 'whitespace' or 'comment'.
        parent_type (`ParentItem` | None): A `ParentItem` instance, corresponding
            to a string literal representing the type of the parent of the
            styling. Can be None if there is no parent. 
        style (str): The string value of the style.
        hierarchy (`Hierarchy` | None): A `Hierarchy` instance representing the
            full hierarchy of the structure.
        line_no (int): An integer line number marking the beginning of the
            styling.
        container_pos (int): An integer position of the styling amongst all
            other types, including stylings (whitespace, comments), within the
            parent.
        from_aot (bool): A boolean indicating whether the styling is nested
            within an array of tables.
    """
    item_type: StyleItem
    parent_type: Optional[ParentItem]
    style: str
    hierarchy: Optional[Hierarchy]
    line_no: int
    container_pos: int
    from_aot: bool = False