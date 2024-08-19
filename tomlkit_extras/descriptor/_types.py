from __future__ import annotations
from dataclasses import dataclass
import copy
from typing import (
    Any,
    cast,
    Dict,
    List,
    Literal,
    Optional,
    Union
)

from tomlkit.container import OutOfOrderTableProxy
from tomlkit import items

from tomlkit_extras.descriptor._helpers import get_item_type
from tomlkit_extras.descriptor._create import create_comment_descriptor
from tomlkit_extras.descriptor._descriptors import CommentDescriptor
from tomlkit_extras._hierarchy import Hierarchy
from tomlkit_extras._typing import (
    ContainerInOrder,
    ContainerItemDecomposed,
    DescriptorInput,
    FieldItem,
    Item,
    ParentItem,
    StyleItem,
    Stylings,
    Table,
    TableItem
)

@dataclass(frozen=True)
class BaseItem(object):
    """"""
    info: TOMLItemInfo


@dataclass(frozen=True)
class StylingInfo(BaseItem):
    """"""
    item: Stylings


@dataclass(frozen=True)
class ContainerInfo(BaseItem):
    """"""
    item: ContainerInOrder


@dataclass(frozen=True)
class TableInfo(BaseItem):
    """"""
    item: Table


@dataclass(frozen=True)
class FieldInfo(BaseItem):
    """"""
    item: items.Item


@dataclass
class ItemType:
    """"""
    item_type: Item
    parent_type: Optional[ParentItem]


@dataclass(frozen=True)
class StylingPosition:
    """"""
    item_type: StyleItem
    style: str
    line_no: int
    container: int


@dataclass
class ArrayOfTables:
    """"""
    aots: List[ArrayOfTablesPosition]

    array_indices: Dict[str, int]

    def get_array(self, hierarchy: str) -> ArrayOfTablesPosition:
        """"""
        return self.aots[self.array_indices[hierarchy]]

    def update_arrays(self, hierarchy: str, array: ArrayOfTablesPosition) -> None:
        """"""
        self.array_indices[hierarchy] += 1
        self.aots.append(array)


@dataclass
class ArrayOfTablesPosition:
    """"""
    item_type: Literal['array-of-tables']
    parent_type: Optional[ParentItem]
    name: str
    line_no: int
    position: ItemPosition
    tables: Dict[str, List[TablePosition]]

    table_indices: Dict[str, int]

    def get_table(self, hierarchy: str) -> TablePosition:
        """"""
        return self.tables[hierarchy][self.table_indices[hierarchy]]

    def update_tables(self, hierarchy: str, table_position: TablePosition) -> None:
        """"""        
        if hierarchy not in self.tables:
            self.tables[hierarchy] = [table_position]
            self.table_indices[hierarchy] = 0
        else:
            self.tables[hierarchy].append(table_position)
            self.table_indices[hierarchy] += 1


@dataclass
class StylingPositions:
    """"""
    comments: Dict[str, List[StylingPosition]]
    whitespace: Dict[str, List[StylingPosition]]

    def update_stylings(self, style: StylingInfo, position: ItemPosition, line_no: int) -> None:
        """"""
        styling_value: str

        if isinstance(style.item, items.Comment):
            styling_value = style.item.trivia.comment
            current_source = self.comments
        else:
            styling_value = style.item.value
            current_source = self.whitespace

        styling_position = StylingPosition(
            item_type=cast(StyleItem, style.info.item_type.item_type),
            style=styling_value,
            line_no=line_no,
            container=position.container
        )
        if styling_value not in current_source:
            current_source[styling_value] = [styling_position]
        else:
            current_source[styling_value].append(styling_position)


@dataclass
class FieldPosition:
    """"""
    item_type: FieldItem
    line_no: int
    position: ItemPosition
    value: Any
    comment: Optional[CommentDescriptor]
    styling: StylingPositions

    @classmethod
    def from_toml_item(cls, item: FieldInfo, line_no: int, position: ItemPosition) -> FieldPosition:
        """"""
        comment_line_no: Optional[int]
        styling = StylingPositions(comments=dict(), whitespace=dict())
        if isinstance(item.item, items.Array):
            comment_line_no = None
        else:
            comment_line_no = TablePosition.find_comment_line_no(line_no=line_no, item=item.item)

        comment = create_comment_descriptor(item=item.item, line_no=comment_line_no)
        return cls(
            line_no=line_no,
            item_type=cast(FieldItem, item.info.item_type.item_type),
            position=copy.copy(position),
            value=item.item.unwrap(),
            comment=comment,
            styling=styling
        )
    
    def update_comment(self, item: items.Array, line_no: int) -> None:
        """"""
        comment_line_no = TablePosition.find_comment_line_no(line_no=line_no, item=item)
        self.comment = create_comment_descriptor(item=item, line_no=comment_line_no)


@dataclass(frozen=True)
class TOMLItemInfo:
    """"""
    item_type: ItemType
    key: str
    hierarchy: str

    @property
    def full_hierarchy(self) -> str:
        """"""
        return Hierarchy.create_hierarchy(hierarchy=self.hierarchy, update=self.key)

    @classmethod
    def from_parent_type(
        cls, key: str, hierarchy: str, toml_item: DescriptorInput, parent_type: Optional[ParentItem] = None
    ) -> TOMLItemInfo:
        """"""
        item_type = ItemType(item_type=get_item_type(toml_item=toml_item), parent_type=parent_type)
        return cls(item_type=item_type, key=key, hierarchy=hierarchy)

    @classmethod
    def from_body_item(
        cls, hierarchy: str, container_info: TOMLItemInfo, body_item: ContainerItemDecomposed
    ) -> TOMLItemInfo:
        """"""
        item_key, toml_item = body_item
        item_type = ItemType(
            item_type=get_item_type(toml_item=toml_item),
            parent_type=cast(ParentItem, container_info.item_type.item_type)
        )

        return cls(
            item_type=item_type, key=item_key or '', hierarchy=hierarchy
        )


@dataclass
class ItemPosition:
    """"""
    attribute: int
    container: int

    def update_position(self) -> None:
        """"""
        self.attribute += 1

    def update_body_position(self) -> None:
        """"""
        self.container += 1

    def update_positions(self) -> None:
        self.update_position()
        self.update_body_position()


@dataclass
class TablePosition:
    """"""
    item_type: TableItem
    parent_type: Optional[ParentItem]
    line_no: int
    position: ItemPosition
    comment: Optional[CommentDescriptor]
    styling: StylingPositions
    fields: Dict[str, FieldPosition]

    @staticmethod
    def find_comment_line_no(line_no: int, item: items.Item) -> Optional[int]:
        """"""
        comment_position: Optional[int]

        if not item.trivia.comment:
            comment_position = None
        else:
            ws_before_comment: str = item.trivia.indent + item.trivia.comment_ws
            num_newlines = ws_before_comment.count('\n')
            comment_position = line_no + num_newlines

        return comment_position

    @classmethod
    def from_table_item(cls, line_no: int, position: ItemPosition, table: TableInfo) -> TablePosition:
        """"""
        comment_line_no = TablePosition.find_comment_line_no(line_no=line_no, item=table.item)
        styling = StylingPositions(comments=dict(), whitespace=dict())
        comment = create_comment_descriptor(item=table.item, line_no=comment_line_no)
        return cls(
            line_no=line_no,
            item_type=cast(TableItem, table.info.item_type.item_type),
            parent_type=table.info.item_type.parent_type,
            comment=comment,
            position=copy.copy(position),
            styling=styling,
            fields=dict()
        )
        
    def add_field(self, item: FieldInfo, line_no: int, position: ItemPosition) -> None:
        """"""
        field_position = FieldPosition.from_toml_item(item=item, line_no=line_no, position=position)
        self.fields.update({item.info.key: field_position})


class TOMLStatistics:
    """"""
    def __init__(self) -> None:
        self._number_of_tables = 0
        self._number_of_inline_tables = 0
        self._number_of_aots = 0
        self._number_of_comments = 0
        self._number_of_fields = 0
        self._number_of_arrays = 0

    def add_table(self, table: items.Table) -> None:
        """"""
        if not (isinstance(table, items.Table) and table.is_super_table()):
            self._number_of_tables += 1
            self.add_comment(item=table)

    def add_inline_table(self, table: items.InlineTable) -> None:
        """"""
        self._number_of_inline_tables += 1
        self.add_comment(item=table)

    def add_array(self, item: items.Array) -> None:
        """"""
        self._number_of_arrays += 1
        self.add_comment(item=item)

    def add_aot(self) -> None:
        """"""
        self._number_of_aots += 1

    def add_comment(self, item: items.Item) -> None:
        """"""
        if (
            isinstance(item, items.Comment) or
            (not isinstance(item, items.Whitespace) and item.trivia.comment)
        ):
            self._number_of_comments += 1

    def add_field(self, item: items.Item) -> None:
        """"""
        self._number_of_fields += 1
        self.add_comment(item=item)