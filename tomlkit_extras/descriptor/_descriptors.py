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
    """"""
    comment: str
    line_no: int


@dataclass(frozen=True)
class Descriptor(object):
    """"""
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
    """"""
    item_type: TableItem
    fields: Dict[str, FieldDescriptor]
    child_tables: Optional[Set[Hierarchy]]


@dataclass(frozen=True)
class ArrayOfTablesDescriptor(Descriptor):
    """"""
    tables: List[TableDescriptor]
    item_type: Literal['array-of-tables'] = 'array-of-tables'


@dataclass(frozen=True)
class FieldDescriptor(Descriptor):
    """"""
    item_type: FieldItem
    value: Any

    @property
    def value_type(self) -> Type[Any]:
        """"""
        return type(self.value)


@dataclass(frozen=True)
class StyleDescriptor:
    """"""
    item_type: StyleItem
    parent_type: Optional[ParentItem]
    style: str
    hierarchy: Optional[Hierarchy]
    line_no: int
    container_pos: int
    from_aot: bool = False