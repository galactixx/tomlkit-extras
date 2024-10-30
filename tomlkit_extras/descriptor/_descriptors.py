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
    Set,
    Type,
    TYPE_CHECKING
)

from tomlkit import items

from tomlkit_extras._utils import find_comment_line_no
from tomlkit_extras._hierarchy import Hierarchy
from tomlkit_extras.descriptor._helpers import create_comment_descriptor
from tomlkit_extras._typing import (
    AoTItem,
    FieldItem,
    Item,
    ParentItem,
    StyleItem,
    Table,
    TableItem
)

if TYPE_CHECKING:
    from tomlkit_extras.descriptor._types import (
        ItemInfo,
        ItemPosition,
        StylingDescriptors
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


class AbstractDescriptor(ABC):
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
    def __init__(self, item_info: ItemInfo, position: ItemPosition) -> None:
        self._item_info = item_info
        self._position = position

    @property
    @abstractmethod
    def item_type(self) -> Item:
        """"""
        raise NotImplementedError("This method must be overridden by subclasses")

    @property
    def name(self) -> str:
        """"""
        return self._item_info.key

    @property
    def hierarchy(self) -> Hierarchy:
        """"""
        hierarchy = Hierarchy.from_str_hierarchy(self._item_info.hierarchy)
        hierarchy.add_to_hierarchy(update=self.name)
        return hierarchy
    
    @property
    def attribute_position(self) -> int:
        """"""
        return self._position.attribute
    
    @property
    def container_position(self) -> int:
        """"""
        return self._position.container

    @property
    def parent_type(self) -> Optional[ParentItem]:
        """"""
        return self._item_info.parent_type


class FieldDescriptor(AbstractDescriptor):
    """
    A class which provides detail on a field, a key-value pair
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
    def __init__(
        self,
        line_no: int,
        info: ItemInfo,
        position: ItemPosition,
        value: Any,
        comment: Optional[CommentDescriptor],
        styling: StylingDescriptors
    ):
        super().__init__(item_info=info, position=position)
        self.line_no = line_no
        self.value = value
        self.comment = comment
        self.styling = styling

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
        styling = StylingDescriptors(comments=dict(), whitespace=dict())
        if isinstance(item, items.Array):
            comment_line_no = None
        else:
            comment_line_no = find_comment_line_no(line_no=line_no, item=item)

        comment = create_comment_descriptor(item=item, line_no=comment_line_no)
        position = copy.copy(position)
        value = item.unwrap()
        return cls(
            line_no=line_no,
            info=info,
            position=position,
            value=value,
            comment=comment,
            styling=styling
        )
    
    def _update_comment(self, item: items.Array, line_no: int) -> None:
        """"""
        comment_line_no = find_comment_line_no(line_no=line_no, item=item)
        self.comment = create_comment_descriptor(item=item, line_no=comment_line_no)


class TableDescriptor(AbstractDescriptor):
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
    def __init__(
        self,
        line_no: int,
        info: ItemInfo,
        position: ItemPosition,
        comment: Optional[CommentDescriptor],
        styling: StylingDescriptors
    ):
        super().__init__(item_info=info, position=position)
        self.line_no = line_no
        self.comment = comment
        self.styling = styling

        self._fields: Dict[str, FieldDescriptor] = dict()
        self._child_tables: Optional[Set[str]] = None

    @property
    def child_tables(self) -> Optional[Set[str]]:
        """"""
        return self._child_tables
    
    @property
    def fields(self) -> Dict[str, FieldDescriptor]:
        """"""
        return self._fields

    @property
    def item_type(self) -> TableItem:
        """"""
        return cast(TableItem, self._item_info.item_type)

    @classmethod
    def from_table_item(
        cls, table: Table, info: ItemInfo, position: ItemPosition, line_no: int
    ) -> TableDescriptor:
        """"""
        comment_line_no = find_comment_line_no(line_no=line_no, item=table)
        styling = StylingDescriptors(comments=dict(), whitespace=dict())
        comment = create_comment_descriptor(item=table, line_no=comment_line_no)
        position = copy.copy(position)
        return cls(
            line_no=line_no,
            info=info,
            position=position,
            comment=comment,
            styling=styling
        )

    def _update_child_tables(self, tables: Set[str]) -> None:
        """"""
        if self._child_tables is None:
            self._child_tables = tables
        else:
            self._child_tables = self._child_tables.union(tables)

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


class ArrayOfTablesDescriptor(AbstractDescriptor):
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

    def _update_tables(self, hierarchy: str, table_position: TableDescriptor) -> None:
        """"""        
        if hierarchy not in self._tables:
            self._tables[hierarchy] = [table_position]
            self._table_indices[hierarchy] = 0
        else:
            self._tables[hierarchy].append(table_position)
            self._table_indices[hierarchy] += 1