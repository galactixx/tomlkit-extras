from typing import (
    Literal,
    TypeAlias,
    Union
)

from tomlkit.container import OutOfOrderTableProxy
from tomlkit import items, TOMLDocument

from tomlkit_extensions.hierarchy import Hierarchy

# General types
TOMLHierarchy: TypeAlias = Union[str, Hierarchy]
TOMLSource: TypeAlias = Union[TOMLDocument, items.Table, items.AoT]

TOMLTable: TypeAlias = Union[items.Table, items.InlineTable]

TOMLTableLike: TypeAlias = Union[
    items.Table, 
    items.InlineTable, 
    items.AoT,
    OutOfOrderTableProxy
]

TOMLContainer: TypeAlias = Union[
    TOMLDocument, 
    items.Table,
    items.InlineTable,
    items.Array,
    OutOfOrderTableProxy
]

# Descriptor types
TOMLType: TypeAlias = Literal[
    'document',
    'field',
    'table',
    'inline-table',
    'super-table',
    'array',
    'array-of-tables',
    'whitespace',
    'comment'
]
Item: TypeAlias = Literal[
    'field',
    'table',
    'inline-table',
    'array',
    'whitespace',
    'comment'
]
ParentItem: TypeAlias = Literal[
    'document', 
    'table',
    'inline-table',
    'super-table',
    'array',
    'array-of-tables'
]

StyleItem: TypeAlias = Literal['whitespace', 'comment']
TableItem: TypeAlias = Literal['table', 'inline-table']
FieldItem: TypeAlias = Literal['field', 'array']