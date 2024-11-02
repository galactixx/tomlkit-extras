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
from tomlkit_extras.descriptor._helpers import create_comment_descriptor
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
class ArrayOfTablesDescriptors:
    """
    """
    aots: List[ArrayOfTablesDescriptor]

    array_indices: Dict[str, int]

    def get_array(self, hierarchy: str) -> ArrayOfTablesDescriptor:
        """"""
        return self.aots[self.array_indices[hierarchy]]

    def update_arrays(self, hierarchy: str, array: ArrayOfTablesDescriptor) -> None:
        """"""
        self.array_indices[hierarchy] += 1
        self.aots.append(array)


@dataclass
class StylingDescriptors:
    """"""
    comments: Dict[str, List[StyleDescriptor]]
    whitespace: Dict[str, List[StyleDescriptor]]

    def update_stylings(
        self, style: Stylings, info: ItemInfo, position: ItemPosition, line_no: int
    ) -> None:
        """"""
        styling_value: str

        if isinstance(style, items.Comment):
            styling_value = style.trivia.comment
            current_source = self.comments
        else:
            styling_value = style.value
            current_source = self.whitespace

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


@dataclass(frozen=True)
class CommentDescriptor:
    """
    A dataclass which provides detail for a comment that is directly
    associated with a particular field or table.

    Attributes:
        comment (str): A string representing the comment.
        line_no (int): An integer line number where the comment is located.
    """
    comment: str
    line_no: int


class AbstractDescriptor(ABC):
    """
    Base descriptor class, which provides no functionality, but a series
    of common attributes for all sub-classes, those being `TableDescriptor`,
    `ArrayOfTablesDescriptor`, `StyleDescriptor`, and `FieldDescriptor`.
    
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
        raise NotImplementedError("This method must be overridden by subclasses")

    @property
    def from_aot(self) -> bool:
        """
        Returns a boolean indicating whether the structure is located within an
        array of tables.
        """
        return self._item_info.from_aot

    @property
    def hierarchy(self) -> Hierarchy:
        """Returns the hierarchy of the TOML structure."""
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
    ar similear to that of an "attribute". These are fields, tables, or array of tables.

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
    - parent_type
    - name
    - hierarchy
    - attribute_position
    - container_position
    - from_aot

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
        """"""
        return cast(FieldItem, self._item_info.item_type)

    @property
    def value_type(self) -> Type[Any]:
        """"""
        return type(self.value)

    @classmethod
    def _from_toml_item(
        cls, item: items.Item, info: ItemInfo, line_no: int, position: ItemPosition
    ) -> FieldDescriptor:
        """"""
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
        """"""
        comment_line_no = find_comment_line_no(line_no=line_no, item=item)
        self.comment = create_comment_descriptor(item=item, line_no=comment_line_no)


class TableDescriptor(AttributeDescriptor):
    """
    A dataclass which provides detail on a table or inline table, a key-value
    pair that can contain nested key-value pairs.

    Inherits properties from `AttributeDescriptor`:
    - parent_type
    - name
    - hierarchy
    - attribute_position
    - container_position
    - from_aot

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
        """"""
        return self._fields

    @property
    def item_type(self) -> TableItem:
        """"""
        return cast(TableItem, self._item_info.item_type)

    @classmethod
    def _from_table_item(
        cls, table: Table, info: ItemInfo, position: ItemPosition, line_no: int
    ) -> TableDescriptor:
        """"""
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
        """"""
        field_descriptor = FieldDescriptor._from_toml_item(
            item=item, info=info, line_no=line_no, position=position
        )
        self._fields.update({info.key: field_descriptor})


class StyleDescriptor(AbstractDescriptor):
    """
    A dataclass which provides detail on a specific styling appearing in a
    tomlkit type instance.

    A styling can either be a comment, represented in tomlkit as a
    tomlkit.items.Comment instance, or a whitespace, represented as a
    tomlkit.items.Whitespace instance.

    These are comments or whitespaces that are not directly associated with
    a field or table, but are contained within tomlkit structures like tables. 

    Inherits properties from `AbstractDescriptor`:
    - parent_type
    - hierarchy
    - container_position
    - from_aot

    Attributes:
        item_type (`StyleItem`): A `StyleItem` instance, corresponding to a
            string literal representing the type of the styling, being
            either 'whitespace' or 'comment'.
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
    def item_type(self) -> StyleItem:
        """"""
        return cast(StyleItem, self._item_info.item_type)


class ArrayOfTablesDescriptor(AttributeDescriptor):
    """
    A dataclass which provides detail on an array of tables, a list of
    tables.

    Inherits properties from `AttributeDescriptor`:
    - parent_type
    - name
    - hierarchy
    - attribute_position
    - container_position
    - from_aot

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
        """"""
        return cast(AoTItem, self._item_info.item_type)
    
    @property
    def tables(self) -> Dict[str, List[TableDescriptor]]:
        """"""
        return self._tables

    def _get_table(self, hierarchy: str) -> TableDescriptor:
        """"""
        return self._tables[hierarchy][self._table_indices[hierarchy]]

    def _update_tables(self, hierarchy: str, table_descriptor: TableDescriptor) -> None:
        """"""        
        if hierarchy not in self._tables:
            self._tables[hierarchy] = [table_descriptor]
            self._table_indices[hierarchy] = 0
        else:
            self._tables[hierarchy].append(table_descriptor)
            self._table_indices[hierarchy] += 1