from __future__ import annotations
from dataclasses import dataclass
import copy
from typing import (
    Any,
    cast,
    Dict,
    List,
    Optional,
    Tuple,
    Union
)

from tomlkit.container import OutOfOrderTableProxy
from tomlkit import items

from tomlkit_extensions.descriptor._helpers import get_item_type
from tomlkit_extensions.descriptor._create import create_comment_descriptor
from tomlkit_extensions.descriptor._descriptors import CommentDescriptor
from tomlkit_extensions._hierarchy import Hierarchy
from tomlkit_extensions._typing import (
    Container,
    FieldItem,
    Item,
    ParentItem,
    StyleItem,
    TableItem,
    TOMLType
)

@dataclass(frozen=True)
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
    item_type: TableItem
    parent_type: ParentItem
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

    def update_stylings(
        self, style_item: TOMLItem, position: ItemPosition, line_no: int
    ) -> None:
        """"""
        style = cast(Union[items.Comment, items.Whitespace], style_item.item)

        if isinstance(style, items.Comment):
            styling = style.trivia.comment
            current_source = self.comments
        else:
            styling = style.value
            current_source = self.whitespace

        styling_position = StylingPosition(
            item_type=cast(StyleItem, style_item.item_type.item_type),
            style=styling,
            line_no=line_no,
            container=position.container
        )
        if styling not in current_source:
            current_source[styling] = [styling_position]
        else:
            current_source[styling].append(styling_position)


@dataclass
class FieldPosition:
    """"""
    item_type: FieldItem
    line_no: int
    position: ItemPosition
    value: Any
    comment: Optional[CommentDescriptor]
    styling: Optional[StylingPositions]

    @classmethod
    def from_toml_item(cls, line_no: int, position: ItemPosition, item: TOMLItem) -> FieldPosition:
        """"""
        if isinstance(item.item, items.Array):
            styling = StylingPositions(comments=dict(), whitespace=dict())
            comment_line_no = None
        else:
            styling = None
            comment_line_no = TablePosition.find_comment_line_no(line_no=line_no, item=item.item)

        comment = create_comment_descriptor(item=item.item, line_no=comment_line_no)
        return cls(
            line_no=line_no,
            item_type=cast(FieldItem, item.item_type.item_type),
            position=copy.copy(position),
            value=item.item.unwrap(),
            comment=comment,
            styling=styling
        )

    def update_comment(self, item: TOMLItem, line_no: int) -> None:
        """"""
        comment_position = TablePosition.find_comment_line_no(line_no=line_no, item=item.item)
        self.comment = comment_position


@dataclass(frozen=True)
class ContainerItem:
    """"""
    item_type: ItemType
    key: Optional[str]
    hierarchy: str
    item: Container

    @classmethod
    def from_toml_item(cls, item: TOMLItem) -> ContainerItem:
        """"""
        return cls(
            item_type=item.item_type,
            key=item.key,
            hierarchy=item.hierarchy,
            item=cast(Container, item.item)
        )


@dataclass(frozen=True)
class TOMLItem:
    """"""
    item_type: ItemType
    key: Optional[str]
    hierarchy: str
    item: items.Item

    @property
    def full_hierarchy(self) -> str:
        """"""
        return Hierarchy.create_hierarchy(hierarchy=self.hierarchy, update=self.key)

    @classmethod
    def from_parent_type(
        cls, key: str, hierarchy: str, toml_item: items.Item, parent_type: Optional[TOMLType] = None
    ) -> TOMLItem:
        """"""
        item_type = ItemType(
            item_type=get_item_type(toml_item=toml_item), parent_type=parent_type
        )
        return cls(
            item_type=item_type, key=key, hierarchy=hierarchy, item=toml_item
        )

    @classmethod
    def from_body_item(
        cls,
        hierarchy: str,
        body_item: Tuple[Optional[items.Key], items.Item],
        container: ContainerItem
    ) -> TOMLItem:
        """"""
        item_key: Optional[str] = (
            body_item[0].as_string().strip() if body_item[0] is not None else None
        )
        toml_item: items.Item = body_item[1]

        item_type = ItemType(
            item_type=get_item_type(toml_item=toml_item),
            parent_type=container.item_type.item_type
        )

        return cls(
            item_type=item_type, key=item_key, hierarchy=hierarchy, item=toml_item
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
    parent_type: ParentItem
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
    def from_table_item(
        cls, line_no: int, position: ItemPosition, container: ContainerItem
    ) -> TablePosition:
        """"""
        comment_line_no = TablePosition.find_comment_line_no(line_no=line_no, item=container.item)
        styling = StylingPositions(comments=dict(), whitespace=dict())
        comment = create_comment_descriptor(item=container.item, line_no=comment_line_no)
        return cls(
            line_no=line_no,
            item_type=cast(TableItem, container.item_type.item_type),
            parent_type=container.item_type.parent_type,
            comment=comment,
            position=copy.copy(position),
            styling=styling,
            fields=dict()
        )
        
    def add_field(self, item: TOMLItem, line_no: int, position: ItemPosition) -> None:
        """"""
        field_position = FieldPosition.from_toml_item(line_no=line_no, position=position, item=item)
        self.fields.update({item.key: field_position})


class TOMLStatistics:
    """"""
    def __init__(self):
        self._number_of_tables = 0
        self._number_of_inline_tables = 0
        self._number_of_aots = 0
        self._number_of_comments = 0
        self._number_of_fields = 0
        self._number_of_arrays = 0

    def add_table(self, table: Union[items.Table, OutOfOrderTableProxy]) -> None:
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