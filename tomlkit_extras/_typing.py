from typing import (
    List,
    Literal,
    Optional,
    Tuple,
    TypeAlias,
    Union
)

from tomlkit.container import OutOfOrderTableProxy
from tomlkit import items, TOMLDocument

from tomlkit_extras._hierarchy import Hierarchy

ContainerComments: TypeAlias = Tuple[int, int, str]

# General types
TOMLHierarchy: TypeAlias = Union[str, Hierarchy]
TOMLSource: TypeAlias = Union[TOMLDocument, items.Table, items.AoT, OutOfOrderTableProxy]

TOMLDictLike: TypeAlias = Union[TOMLDocument, items.Table, items.InlineTable, OutOfOrderTableProxy]
Table: TypeAlias = Union[items.Table, items.InlineTable]

ContainerItemDecomposed: TypeAlias = Tuple[Optional[str], items.Item]

TOMLValidReturn: TypeAlias = Union[TOMLDocument, OutOfOrderTableProxy, items.Item]
Retrieval: TypeAlias = Union[OutOfOrderTableProxy, items.Item, List[items.Item]]

ContainerBodyItem: TypeAlias = Tuple[Optional[items.Key], items.Item]
ContainerBody: TypeAlias = List[ContainerBodyItem]

HasComments: TypeAlias = Union[
    TOMLDocument,
    items.Table,
    items.Array,
    items.AoT,
    OutOfOrderTableProxy
]

Container: TypeAlias = Union[
    TOMLDocument, 
    items.Table,
    items.InlineTable,
    items.Array,
    OutOfOrderTableProxy
]

ContainerLike: TypeAlias = Union[
    TOMLDocument, 
    items.Table,
    items.InlineTable,
    items.Array,
    items.AoT,
    OutOfOrderTableProxy
]

# Descriptor types
Item: TypeAlias = Literal[
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
ChildItem: TypeAlias = Literal[
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
TopLevelItem: TypeAlias = Literal['document', 'table', 'array-of-tables']