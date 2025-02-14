import sys
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

_IS_PY_3_10 = sys.version_info >= (3, 10)

if _IS_PY_3_10:
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

from tomlkit import TOMLDocument, items
from tomlkit.container import OutOfOrderTableProxy

from tomlkit_extras._hierarchy import Hierarchy

TOMLSourceFile: TypeAlias = Union[
    str, bytes, bytearray, Path, TOMLDocument, Dict[str, Any]
]

# The return type of get_comments function, returning a tuple where the first item
# is the line number where the comment is located and the second is the comment
ContainerComment: TypeAlias = Tuple[int, str]

# Tomlkit types that are subclasses of dictionaries
TOMLDictLike: TypeAlias = Union[
    TOMLDocument, items.Table, items.InlineTable, OutOfOrderTableProxy
]

# Tomlkit types that are tables
Table: TypeAlias = Union[items.Table, items.InlineTable]

# Tomlkit types that are classified as styles/stylings
Stylings: TypeAlias = Union[items.Whitespace, items.Comment]

# Valid tomlkit return types when traversing a TOMLDocument
TOMLValidReturn: TypeAlias = Union[OutOfOrderTableProxy, items.Item]

# Valid tomlkit return types from the get_attribute_from_toml_source function
Retrieval: TypeAlias = Union[TOMLValidReturn, List[items.Item]]

# Valid hierarchy types in most functions in package
TOMLHierarchy: TypeAlias = Union[str, Hierarchy]

# Various types that have to do with tomlkit types that contain a body of fields,
# tables, and stylings.
BodyContainerItem: TypeAlias = Tuple[Optional[items.Key], items.Item]
BodyContainerItems: TypeAlias = List[BodyContainerItem]
BodyContainerItemDecomposed: TypeAlias = Tuple[Optional[str], items.Item]
BodyContainer: TypeAlias = Union[
    TOMLDocument, items.Table, items.InlineTable, items.Array, OutOfOrderTableProxy
]
BodyContainerInOrder: TypeAlias = Union[
    TOMLDocument, items.Table, items.InlineTable, items.Array
]

# Tomlkit types that can contain key-value pairs
TOMLFieldSource: TypeAlias = Union[
    TOMLDocument, items.Table, items.InlineTable, items.AoT, OutOfOrderTableProxy
]

# Valid input tomlkit types for most TOML related functions in package
TOMLSource: TypeAlias = Union[
    TOMLDocument, items.Table, items.AoT, OutOfOrderTableProxy
]

# Valid input tomlkit types for the TOMLDocumentDescriptor class
DescriptorInput: TypeAlias = Union[TOMLDocument, items.Table, items.AoT, items.Array]

# Tomlkit types that can have comments in the top-level space
AnnotatedContainer: TypeAlias = Union[
    TOMLDocument, items.Table, items.Array, OutOfOrderTableProxy
]

# Any tomlkit type that can contain other objects nested within
ContainerLike: TypeAlias = Union[
    TOMLDocument,
    items.Table,
    items.Array,
    OutOfOrderTableProxy,
    items.AoT,
    items.InlineTable,
]

# Literals identifying the TOML item type for a given descriptor
StyleItem: TypeAlias = Literal["whitespace", "comment"]
TableItem: TypeAlias = Literal["table", "inline-table"]
FieldItem: TypeAlias = Literal["field", "array"]
AoTItem: TypeAlias = Literal["array-of-tables"]
TopLevelItem: TypeAlias = Literal["document", "table", "array-of-tables"]
Item: TypeAlias = Literal[
    "document",
    "field",
    "table",
    "inline-table",
    "super-table",
    "array",
    "array-of-tables",
    "whitespace",
    "comment",
]
ParentItem: TypeAlias = Literal[
    "document", "table", "inline-table", "super-table", "array", "array-of-tables"
]
