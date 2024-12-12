from __future__ import annotations

from dataclasses import dataclass
from abc import ABC, abstractmethod
import copy
import re
import itertools
import inspect
from typing import (
    Any,
    cast,
    ClassVar,
    Dict,
    List,
    Optional,
    Set,
    Type,
    TypeVar
)

from tomlkit import items

from tomlkit_extras._exceptions import InvalidStylingError
from tomlkit_extras._utils import (
    find_comment_line_no,
    safe_unwrap
)
from tomlkit_extras._hierarchy import Hierarchy
from tomlkit_extras.descriptor._helpers import (
    CommentDescriptor,
    create_comment_descriptor
)
from tomlkit_extras.descriptor._types import ItemInfo
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

_WHITESPACE_PATTERN = r'^[ \n\r]*$'

Descriptor = TypeVar('Descriptor', bound='AbstractDescriptor')

def _chain_stylings(styles: Dict[str, List[StyleDescriptor]]) -> List[StyleDescriptor]:
    """A private method which flattens a list of lists of `StyleDescriptor` objects."""
    return list(itertools.chain.from_iterable(styles.values()))


def _from_info_to_hierarchy(info: ItemInfo) -> Hierarchy:
    """"""
    hierarchy = Hierarchy.from_str_hierarchy(info.hierarchy)
    hierarchy.add_to_hierarchy(update=info.key)
    return hierarchy


@dataclass
class AoTDescriptors:
    """
    Stores all array-of-tables that have been parsed while recursively
    traversing a TOML structure in the `_generate_descriptor` method of
    `_TOMLParser`.
    """
    aots: List[AoTDescriptor]

    def get_array(self) -> AoTDescriptor:
        """Retrieves the most recent `AoTDescriptor` object added."""
        return self.aots[-1]

    def update_arrays(self, array: AoTDescriptor) -> None:
        """Adds a new `AoTDescriptor` object to existing store."""
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

    @property
    def _decomposed_comments(self) -> List[StyleDescriptor]:
        """Private property that returns a list of the comments store values."""
        return _chain_stylings(styles=self.comments)
        
    @property
    def _decomposed_whitespace(self) -> List[StyleDescriptor]:
        """Private property that returns a list of the whitespace store values."""
        return _chain_stylings(styles=self.whitespace)

    def get_styling(self, styling: str) -> List[StyleDescriptor]:
        """
        Retrieves all stylings, represented by `StyleDescriptor` objects, that
        correspond to a specific string representation.

        Args:
            styling (str): A string representation of a comment or whitespace.

        Returns:
            List[`StyleDescriptor`]: A list of `StyleDescriptor` instances.
        """
        # Check if the string representation of the styling matches the
        # format of a whitespace or text comment
        is_comment = not re.match(_WHITESPACE_PATTERN, styling)

        styling_space = self.comments if is_comment else self.whitespace
        if styling not in styling_space:
            raise InvalidStylingError(
                "Styling does not exist in set of valid stylings",
                set(styling_space.keys())
            )
        
        return styling_space[styling]

    def get_stylings(self, styling: Optional[StyleItem] = None) -> List[StyleDescriptor]:
        """
        Retrieves all stylings, represented by `StyleDescriptor` objects, that
        correspond to a specific string literal.
        
        If "whitespace" is passed all whitespace stylings will be returned. If
        "comment" is passed all comment stylings will be returned. If it is None,
        then all stylings will be returned.

        Args:
            styling (`StyleItem` | None): A literal that identifies the type of
                styling to retrieve. Can be either "whitespace" or "comment".
                Defaults to None.

        Returns:
            List[`StyleDescriptor`]: A list of `StyleDescriptor` instances.
        """
        stylings: List[StyleDescriptor] = []

        if styling != 'comment':
            stylings.extend(self._decomposed_whitespace)

        if styling != 'whitespace':
            stylings.extend(self._decomposed_comments)

        return stylings
        
    def _update_stylings(self, style: Stylings, info: ItemInfo, line_no: int) -> None:
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
            style=styling_value, line_no=line_no, info=info
        )
        if styling_value not in current_source:
            current_source[styling_value] = [styling_position]
        else:
            current_source[styling_value].append(styling_position)


class AbstractDescriptor(ABC):
    __special__: ClassVar[Set[str]] = set()

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
    def __init__(self, item_info: ItemInfo) -> None:
        self._item_info = copy.deepcopy(item_info)

    def copy(self: Descriptor) -> Descriptor:
        """Returns a shallow copy of the object."""
        return copy.copy(self)
    
    def deepcopy(self: Descriptor) -> Descriptor:
        """Returns a deep copy of the object."""
        return copy.deepcopy(self)
    
    def __repr__(self) -> str:
        repr_body: List[str] = []
        all_members: Dict[str, Any] = dict(
            dict(inspect.getmembers(self.__class__)), **self.__dict__
        )

        for member_name, member_value in all_members.items():
            if not member_name.startswith('_') and member_name not in self.__special__:
                if isinstance(member_value, property):
                    member_value = member_value.__get__(self)

                if not callable(member_value):
                    repr_body.append(f'    {member_name}={member_value},\n')
                
        repr_string = f"{self.__class__.__name__}(\n{''.join(repr_body)})"
        return repr_string

    @property
    @abstractmethod
    def item_type(self) -> Item:
        """Returns the type of the structure value."""
        pass

    @property
    @abstractmethod
    def hierarchy(self) -> Optional[Hierarchy]:
        """Returns the hierarchy of the TOML structure as a `Hierarchy` object."""
        pass

    @property
    def from_aot(self) -> bool:
        """
        Returns a boolean indicating whether the structure is located within an
        array of tables.
        """
        return self._item_info.from_aot
    
    @property
    def container_position(self) -> int:
        """
        Returns the position, indexed at 1, of the attribute among other attributes,
        including stylings within its parent.

        Attributes in this case are fields, tables, or arrays.
        """
        return self._item_info.position.container

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
        return self._item_info.position.attribute
    
    @property
    def hierarchy(self) -> Hierarchy:
        """Returns the hierarchy of the TOML structure as a `Hierarchy` object."""
        return _from_info_to_hierarchy(info=self._item_info)


class FieldDescriptor(AttributeDescriptor):
    __special__: ClassVar[Set[str]] = {'stylings'}

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
        value: Any,
        comment: Optional[CommentDescriptor],
        stylings: StylingDescriptors
    ) -> None:
        super().__init__(item_info=info)
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
        cls, item: items.Item, info: ItemInfo, line_no: int
    ) -> FieldDescriptor:
        """
        Private class method which generates an instance of `FieldDescriptor` for
        a given field while recursively traversing a TOML structure in the
        `_generate_descriptor` method of `_TOMLParser`.
        """
        comment_line_no: Optional[int]
        stylings = StylingDescriptors(comments=dict(), whitespace=dict())
        if isinstance(item, items.Array):
            comment_line_no = None
        else:
            comment_line_no = find_comment_line_no(line_no=line_no, item=item)

        comment = create_comment_descriptor(item=item, line_no=comment_line_no)
        value = safe_unwrap(structure=item)
        return cls(
            line_no=line_no,
            info=info,
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
    __special__: ClassVar[Set[str]] = {'stylings', 'fields'}

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
        comment: Optional[CommentDescriptor],
        stylings: StylingDescriptors
    ) -> None:
        super().__init__(item_info=info)
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
    def _from_table_item(cls, table: Table, info: ItemInfo, line_no: int) -> TableDescriptor:
        """
        Private class method which generates an instance of `TableDescriptor` for
        a given table while recursively traversing a TOML structure in the
        `_generate_descriptor` method of `_TOMLParser`.
        """
        comment_line_no = find_comment_line_no(line_no=line_no, item=table)
        stylings = StylingDescriptors(comments=dict(), whitespace=dict())
        comment = create_comment_descriptor(item=table, line_no=comment_line_no)
        return cls(
            line_no=line_no,
            info=info,
            comment=comment,
            stylings=stylings
        )

    def _add_field(self, item: items.Item, info: ItemInfo, line_no: int) -> FieldDescriptor:
        """A private method that adds a field to the existing store of fields."""
        field_descriptor = FieldDescriptor._from_toml_item(
            item=item, info=info, line_no=line_no
        )
        self._fields.update({info.key: field_descriptor})
        return field_descriptor


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
    def __init__(self, style: str, line_no: int, info: ItemInfo) -> None:
        super().__init__(item_info=info)
        self.style = style
        self.line_no = line_no

    @property
    def hierarchy(self) -> Optional[Hierarchy]:
        """Returns the hierarchy of the TOML sstructure as a `Hierarchy` object."""
        if not self._item_info.hierarchy:
            return None
        else:
            return _from_info_to_hierarchy(info=self._item_info)

    @property
    def item_type(self) -> StyleItem:
        """
        Returns a literal identifying the type of the styling as a "comment" or
        "whitespace".
        """
        return cast(StyleItem, self._item_info.item_type)


class AoTDescriptor(AttributeDescriptor):
    __special__: ClassVar[Set[str]] = {'tables'}

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
    def __init__(self, line_no: int, info: ItemInfo) -> None:
        super().__init__(item_info=info)
        self.line_no = line_no

        self._tables: Dict[str, List[TableDescriptor]] = dict()

    @property
    def item_type(self) -> AoTItem:
        """Returns a literal being "array-of-tables"."""
        return cast(AoTItem, self._item_info.item_type)
    
    @property
    def tables(self) -> Dict[str, List[TableDescriptor]]:
        """
        Returns a dictionary containing all tables appearing in the array.
        
        The keys of the dictionary are the string table hierarchies, and the values
        are lists of `TableDescriptor` objects. The values are lists, as within an
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
        tables: Optional[List[TableDescriptor]]

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
        return self._tables[hierarchy][-1]

    def _update_tables(self, hierarchy: str, table_descriptor: TableDescriptor) -> None:
        """A private method that adds a table to the existing store of tables."""    
        if hierarchy not in self._tables:
            self._tables[hierarchy] = [table_descriptor]
        else:
            self._tables[hierarchy].append(table_descriptor)
