from __future__ import annotations

from dataclasses import dataclass
from abc import ABC, abstractmethod
import copy
from typing import (
    Any,
    cast,
    Dict,
    List,
    Optional,
    Type,
    TypeVar
)

from tomlkit import items

from tomlkit_extras._utils import find_comment_line_no
from tomlkit_extras._hierarchy import Hierarchy
from tomlkit_extras.descriptor._helpers import (
    CommentDescriptor,
    create_comment_descriptor
)
from tomlkit_extras.descriptor._types import (
    ItemInfo,
    ItemPosition
)
from tomlkit_extras._typing import (
    AoTItem,
    FieldItem,
    Item,
    ParentItem,
    Stylings,
    StyleItem,
    Table,
    TableItem
)

Descriptor = TypeVar('Descriptor', bound='AbstractDescriptor')

@dataclass
class AoTDescriptors:
    """
    Stores all array-of-tables that have been parsed while recursively
    traversing a TOML structure in the `_generate_descriptor` method of
    `TOMLDocumentDescriptor`.
    """
    aots: List[AoTDescriptor]
    array_indices: Dict[str, int]

    def get_array(self, hierarchy: str) -> AoTDescriptor:
        """
        Retrieves a specific `AoTDescriptor` object, representing an
        array-of-tables, given a string hierarchy.
        """
        return self.aots[self.array_indices[hierarchy]]

    def update_arrays(self, hierarchy: str, array: AoTDescriptor) -> None:
        """
        Adds a new `AoTDescriptor` object to existing store of array-of-tables
        parsed.
        """
        self.array_indices[hierarchy] += 1
        self.aots.append(array)


@dataclass
class StylingDescriptors:
    """
    Provides access to all stylings that existing within a TOML structure.
    These are split up into two main categories, comments and whitespaces.

    Each group is contained in a dictionary where the keys are the string
    representations of the stylings, and the values are the list of
    `StyleDescriptor` objects that correspond to stylings that have that
    specific string.
    
    The values are lists as there can be multiple whitespaces or comments that
    have the same value.

    Attributes:
        comments (Dict[str, List[`StyleDescriptor`]]): A dictionary where the
            keys are string representations of the comments, and the values are
            lists of `StyleDescriptor` corresponding to the comments.
        whitespace (Dict[str, List[`StyleDescriptor`]]): A dictionary where the
            keys are string representations of the whitespaces, and the values
            are lists of `StyleDescriptor` corresponding to the whitespaces.
    """
    comments: Dict[str, List[StyleDescriptor]]
    whitespace: Dict[str, List[StyleDescriptor]]

    def _update_stylings(
        self, style: Stylings, info: ItemInfo, position: ItemPosition, line_no: int
    ) -> None:
        """
        Private method that will create a new `StyleDescriptor` and update the
        existing store of stylings (comments and whitespaces) already parsed.
        """
        styling_value: str # Must always be a string value

        # Based on whether the styling is a comment or a whitespace, a different
        # attribute from that tomlkit type will be assigned to be the value
        # of the styling
        if isinstance(style, items.Comment):
            styling_value = style.trivia.comment
            current_source = self.comments
        else:
            styling_value = style.value
            current_source = self.whitespace

        # Generate a StyleDescriptor object that will be added to the already
        # collected store of stylings
        styling_position = StyleDescriptor(
            style=styling_value,
            line_no=line_no,
            info=info,
            position=position
        )
        if styling_value not in current_source:
            current_source[styling_value] = [styling_position]
        else:
            current_source[styling_value].append(styling_position)


class AbstractDescriptor(ABC):
    """
    Base descriptor class, which provides no functionality, but a series
    of common attributes for all sub-classes, those being `TableDescriptor`,
    `AoTDescriptor`, `StyleDescriptor`, and `FieldDescriptor`.
    
    Properties:
        parent_type (`ParentItem` | None): A `ParentItem` instance, corresponding
            to a string literal representing the type of the parent of the
            structure. Can be None if there is no parent.
        hierarchy (`Hierarchy`): A `Hierarchy` instance representing the full
            hierarchy of the structure.
        container_position (int): An integer position of the structure amongst all
            other types, including stylings (whitespace, comments), within the
            parent.
        from_aot (bool): A boolean indicating whether the structure is nested
            within an array of tables.
    """
    def __init__(self, item_info: ItemInfo, position: ItemPosition) -> None:
        self._item_info = item_info
        self._position = copy.copy(position)

    def copy(self) -> Descriptor:
        """Returns a shallow copy of the object."""
        return copy.copy(self)
    
    def deepcopy(self) -> Descriptor:
        """Returns a deep copy of the object."""
        return copy.deepcopy(self)

    @property
    @abstractmethod
    def item_type(self) -> Item:
        """Returns the type of the structure value."""
        pass

    @property
    def from_aot(self) -> bool:
        """
        Returns a boolean indicating whether the structure is located within an
        array of tables.
        """
        return self._item_info.from_aot

    @property
    def hierarchy(self) -> Hierarchy:
        """Returns the hierarchy of the TOML structure as a `Hierarchy` object."""
        hierarchy = Hierarchy.from_str_hierarchy(self._item_info.hierarchy)
        hierarchy.add_to_hierarchy(update=self._item_info.key)
        return hierarchy
    
    @property
    def container_position(self) -> int:
        """
        Returns the position, indexed at 1, of the attribute among other attributes,
        including stylings within its parent.

        Attributes in this case are fields, tables, or arrays.
        """
        return self._position.container

    @property
    def parent_type(self) -> Optional[ParentItem]:
        """
        Returns the type of the parent structure. Can be None if there was no parent.
        """
        return self._item_info.parent_type
    

class AttributeDescriptor(AbstractDescriptor):
    """
    An extension of the `AbstractDescriptor` which is built for structures who
    ar similear to that of an "attribute". These are fields, tables, or array of
    tables.

    Properties:
        name (str): The name of the attribute (field, table, or array of tables).
        attribute_position (int): An integer position of the structure amongst all
            other key value pairs (fields, tables) within the parent.
    """
    @property
    def name(self) -> str:
        """Returns the name of the TOML structure."""
        return self._item_info.key

    @property
    def attribute_position(self) -> int:
        """
        Returns the position, indexed at 1, of the attribute among other attributes
        within its parent.

        Attributes in this case are fields, tables, or arrays.
        """
        return self._position.attribute
    

class FieldDescriptor(AttributeDescriptor):
    """
    A class which provides detail on a field, a key-value pair that cannot
    contain nested key-value pairs.

    Inherits properties from `AttributeDescriptor`:
    - `parent_type`
    - `name`
    - `hierarchy`
    - `attribute_position`
    - `container_position`
    - `from_aot`

    Attributes:
        item_type (`FieldItem`): A `FieldItem` instance, corresponding to a
            string literal representing the type of the table, being
            either 'field' or 'array'.
        line_no (int): An integer line number marking the beginning of the
            structure.
        value (Any): The value of the field.
        value_type (Type[Any]): The type of the field value.
        comment (`CommentDescriptor` | None): A `CommentDescriptor` instance,
            correspondng to the comment associated with the structure. Can
            be None if there is no comment.
        stylings (`StylingDescriptors`): An object with all stylings associated
            with the field.
    """
    def __init__(
        self,
        line_no: int,
        info: ItemInfo,
        position: ItemPosition,
        value: Any,
        comment: Optional[CommentDescriptor],
        stylings: StylingDescriptors
    ):
        super().__init__(item_info=info, position=position)
        self.line_no = line_no
        self.value = value
        self.comment = comment
        self.stylings = stylings

    @property
    def item_type(self) -> FieldItem:
        """
        Returns a literal identifying the type of the field as an "array" or
        "field" (non-array).
        """
        return cast(FieldItem, self._item_info.item_type)

    @property
    def value_type(self) -> Type[Any]:
        """Returns the type of the field value."""
        return type(self.value)

    @classmethod
    def _from_toml_item(
        cls, item: items.Item, info: ItemInfo, line_no: int, position: ItemPosition
    ) -> FieldDescriptor:
        """
        Private class method which generates an instance of `FieldDescriptor` for
        a given field while recursively traversing a TOML structure in the
        `_generate_descriptor` method of `TOMLDocumentDescriptor`.
        """
        comment_line_no: Optional[int]
        stylings = StylingDescriptors(comments=dict(), whitespace=dict())
        if isinstance(item, items.Array):
            comment_line_no = None
        else:
            comment_line_no = find_comment_line_no(line_no=line_no, item=item)

        comment = create_comment_descriptor(item=item, line_no=comment_line_no)
        value = item.unwrap()
        return cls(
            line_no=line_no,
            info=info,
            position=position,
            value=value,
            comment=comment,
            stylings=stylings
        )
    
    def _update_comment(self, item: items.Array, line_no: int) -> None:
        """
        A private method that updates a comment attributed to an array field.
        """
        comment_line_no = find_comment_line_no(line_no=line_no, item=item)
        self.comment = create_comment_descriptor(item=item, line_no=comment_line_no)


class TableDescriptor(AttributeDescriptor):
    """
    A dataclass which provides detail on a table or inline table, a key-value
    pair that can contain nested key-value pairs.

    Inherits properties from `AttributeDescriptor`:
    - `parent_type`
    - `name`
    - `hierarchy`
    - `attribute_position`
    - `container_position`
    - `from_aot`

    Attributes:
        item_type (`TableItem`): A `TableItem` instance, corresponding to a
            string literal representing the type of the table, being
            either 'table' or 'inline-table'.
        line_no (int): An integer line number marking the beginning of the
            table.
        fields (Dict[str, `FieldDescriptor`]): A dictionary which has
            key-value pairs each being a field contained in the table. The
            keys are strings representing names of fields (not tables) and
            the corresponding values are `FieldDescriptor` instances.
        num_fields (int): The number of fields contained in table.
        comment (`CommentDescriptor` | None): A `CommentDescriptor` instance,
            correspondng to the comment associated with the structure. Can
            be None if there is no comment.
        stylings (`StylingDescriptors`): An object with all stylings appearing
            within the table.
    """
    def __init__(
        self,
        line_no: int,
        info: ItemInfo,
        position: ItemPosition,
        comment: Optional[CommentDescriptor],
        stylings: StylingDescriptors
    ):
        super().__init__(item_info=info, position=position)
        self.line_no = line_no
        self.comment = comment
        self.stylings = stylings

        self._fields: Dict[str, FieldDescriptor] = dict()

    @property
    def fields(self) -> Dict[str, FieldDescriptor]:
        """
        Returns a dictionary containing all fields appearing in the table.
        
        The keys of the dictionary are the string field names, and the values
        are `FieldDescriptor` objects.
        """
        return self._fields
    
    @property
    def num_fields(self) -> int:
        """Returns the number of fields contained within the table."""
        return len(self._fields)

    @property
    def item_type(self) -> TableItem:
        """
        Returns a literal identifying the type of the table as a "table" or
        "inline-table".
        """
        return cast(TableItem, self._item_info.item_type)

    @classmethod
    def _from_table_item(
        cls, table: Table, info: ItemInfo, position: ItemPosition, line_no: int
    ) -> TableDescriptor:
        """
        Private class method which generates an instance of `TableDescriptor` for
        a given table while recursively traversing a TOML structure in the
        `_generate_descriptor` method of `TOMLDocumentDescriptor`.
        """
        comment_line_no = find_comment_line_no(line_no=line_no, item=table)
        stylings = StylingDescriptors(comments=dict(), whitespace=dict())
        comment = create_comment_descriptor(item=table, line_no=comment_line_no)
        return cls(
            line_no=line_no,
            info=info,
            position=position,
            comment=comment,
            stylings=stylings
        )

    def _add_field(
        self, item: items.Item, info: ItemInfo, position: ItemPosition, line_no: int
    ) -> None:
        """A private method that adds a field to the existing store of fields."""
        field_descriptor = FieldDescriptor._from_toml_item(
            item=item, info=info, line_no=line_no, position=position
        )
        self._fields.update({info.key: field_descriptor})


class StyleDescriptor(AbstractDescriptor):
    """
    A dataclass which provides detail on a specific styling appearing in a
    tomlkit type instance.

    A styling can either be a comment, represented in tomlkit as a
    `tomlkit.items.Comment` instance, or a whitespace, represented as a
    `tomlkit.items.Whitespace` instance.

    These are comments or whitespaces that are not directly associated with
    a field or table, but are contained within tomlkit structures like tables. 

    Inherits properties from `AbstractDescriptor`:
    - `parent_type`
    - `container_position`
    - `from_aot`

    Attributes:
        item_type (`StyleItem`): A `StyleItem` instance, corresponding to a
            string literal representing the type of the styling, being
            either 'whitespace' or 'comment'.
        hierarchy (`Hierarchy` | None): A `Hierarchy` instance representing the full
            hierarchy of the structure, or None if it is a top-level styling.
        style (str): The string value of the style.
        line_no (int): An integer line number marking the beginning of the
            styling.
    """
    def __init__(
        self,
        style: str,
        line_no: int,
        info: ItemInfo,
        position: ItemPosition,
    ) -> None:
        super().__init__(item_info=info, position=position)
        self.style = style
        self.line_no = line_no

    @property
    def hierarchy(self) -> Optional[Hierarchy]:
        """Returns the hierarchy of the TOML structure as a `Hierarchy` object."""
        if not self._item_info.hierarchy:
            return None
        else:
            return super().hierarchy

    @property
    def item_type(self) -> StyleItem:
        """
        Returns a literal identifying the type of the styling as a "comment" or
        "whitespace".
        """
        return cast(StyleItem, self._item_info.item_type)


class AoTDescriptor(AttributeDescriptor):
    """
    A dataclass which provides detail on an array of tables, a list of
    tables.

    Inherits properties from `AttributeDescriptor`:
    - `parent_type`
    - `name`
    - `hierarchy`
    - `attribute_position`
    - `container_position`
    - `from_aot`

    Attributes:
        item_type (`AoTItem`): A `AoTItem` instance, corresponding to a
            string literal representing the structure type.
        line_no (int): An integer line number marking the beginning of the
            array of tables.
        tables (List[`TableDescriptor`]): A list of `TableDescriptor`
            instances where each one represents a table within the array
            of tables.
    """
    def __init__(
        self,
        line_no: int,
        info: ItemInfo,
        position: ItemPosition
    ) -> None:
        super().__init__(item_info=info, position=position)
        self.line_no = line_no

        self._tables: Dict[str, List[TableDescriptor]] = dict()
        self._table_indices: Dict[str, int] = dict()
    
    @property
    def item_type(self) -> AoTItem:
        """Returns a literal being "array-of-tables"."""
        return cast(AoTItem, self._item_info.item_type)
    
    @property
    def tables(self) -> Dict[str, List[TableDescriptor]]:
        """
        Returns a dictionary containing all tables appearing in the array.
        
        The keys of the dictionary are the string table hierarchies, and the values
        are lists of `TableDescriptor` objects. The values are lists as within an
        array-of-tables, there can be multiple tables associated with the same
        hierarchy.
        """
        return self._tables
    
    def num_tables(self, hierarchy: Optional[str] = None) -> int:
        """
        Retrieves the number of tables within the array that is associated
        with a specific hierarchy.

        If no hierarchy is provided, then defaults to None. In this case,
        all tables will be counted and result returned.

        Args:
            hierarchy (str | None): A string representation of a TOML hierarchy.
                Defaults to None.
        
        Returns:
            int: An integer representing the number of tables.
        """
        if hierarchy is None:
            num_tables = 0
            for tables in self._tables.values():
                num_tables += len(tables)
            return num_tables
        else:
            tables = self.tables.get(hierarchy, None)
            return len(tables) if tables is not None else 0

    def _get_table(self, hierarchy: str) -> TableDescriptor:
        """
        A private method that retrieves a specific `TableDescriptor` object,
        representing a table in an array-of-tables, given a string hierarchy.
        """
        return self._tables[hierarchy][self._table_indices[hierarchy]]

    def _update_tables(self, hierarchy: str, table_descriptor: TableDescriptor) -> None:
        """A private method that adds a table to the existing store of tables."""    
        if hierarchy not in self._tables:
            self._tables[hierarchy] = [table_descriptor]
            self._table_indices[hierarchy] = 0
        else:
            self._tables[hierarchy].append(table_descriptor)
            self._table_indices[hierarchy] += 1