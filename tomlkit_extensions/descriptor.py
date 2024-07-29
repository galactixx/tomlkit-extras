from __future__ import annotations
from dataclasses import dataclass
import copy
import re
from typing import (
    Any,
    cast,
    Dict,
    List,
    Literal,
    Optional,
    overload,
    Set,
    Tuple,
    Type,
    TypeAlias,
    Union
)

from tomlkit.container import OutOfOrderTableProxy
from tomlkit import items, TOMLDocument

from tomlkit_extensions.types import Hierarchy
from tomlkit_extensions.exceptions import (
    InvalidArrayOfTablesError,
    InvalidFieldError,
    InvalidHierarchyError,
    InvalidStylingError
)

_Container: TypeAlias = Union[
    TOMLDocument, 
    items.Table,
    items.InlineTable,
    items.Array,
    OutOfOrderTableProxy
]

TomlType: TypeAlias = Literal[
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

def _reorganize_array(array: items.Array) -> List[Tuple[None, items.Item]]:
    """"""
    array_body_items: List[Tuple[None, items.Item]] = []

    for array_item_group in array._value:
        for array_item in array_item_group:
            array_body_items.append((None, array_item))

    return array_body_items


def _find_nested_tables(root_hierarchy: str, hierarchies: Dict[str, Any]) -> Set[Hierarchy]:
    """"""
    return {
        Hierarchy.from_str_hierarchy(hierarchy=hierarchy) for hierarchy in hierarchies
        if root_hierarchy.startswith(hierarchy) and root_hierarchy != hierarchy
    }


def _create_comment_descriptor(item: items.Item, line_no: Optional[int]) -> Optional[CommentDescriptor]:
    """"""
    return (
        CommentDescriptor(comment=item.trivia.comment, line_no=line_no)
        if line_no is not None else None
    )


def _create_style_descriptor(
    styling_position: _StylingPosition, hierarchy: Optional[Hierarchy], parent_type: ParentItem
) -> StyleDescriptor:
    """"""
    return StyleDescriptor(
        item_type=styling_position.item_type,
        parent_type=parent_type,
        style=styling_position.style,
        hierarchy=hierarchy,
        line_no=styling_position.line_no,
        container_pos=styling_position.container,
        from_aot=False
    )


def _create_field_descriptor(
    field: str,
    hierarchy: Hierarchy,
    field_position: _FieldPosition,
    parent_type: ParentItem,
    from_aot: bool
) -> FieldDescriptor:
    """"""
    return FieldDescriptor(
        item_type=field_position.item_type,
        parent_type=parent_type,
        name=field,
        hierarchy=hierarchy,
        line_no=field_position.line_no,
        attribute_pos=field_position.position.attribute,
        container_pos=field_position.position.container,
        comment=field_position.comment,
        from_aot=from_aot,
        value=field_position.value
    )


def _create_table_descriptor(
    hierarchy: Hierarchy, table_position: _TablePosition, tables: Set[Hierarchy], from_aot: bool
) -> TableDescriptor:
    """"""
    fields = {
        field: _create_field_descriptor(
            field=field,
            hierarchy=Hierarchy(hierarchy=hierarchy.hierarchy, attribute=field),
            field_position=field_position,
            parent_type=table_position.item_type,
            from_aot=from_aot
        )
        for field, field_position in table_position.fields.items()
    }

    return TableDescriptor(
        item_type=table_position.item_type,
        parent_type=table_position.parent_type,
        name=hierarchy.attribute,
        hierarchy=hierarchy,
        line_no=table_position.line_no,
        attribute_pos=table_position.position.attribute,
        container_pos=table_position.position.container,
        comment=table_position.comment,
        from_aot=from_aot,
        fields=fields,
        tables=tables or None
    )


def get_item_type(toml_item: items.Item) -> TomlType:
    """"""
    if isinstance(toml_item, TOMLDocument):
        toml_type = 'document'
    elif isinstance(toml_item, (items.Table, OutOfOrderTableProxy)):
        toml_type = 'super-table' if toml_item.is_super_table() else 'table'
    elif isinstance(toml_item, items.InlineTable):
        toml_type = 'inline-table'
    elif isinstance(toml_item, items.Comment):
        toml_type = 'comment'
    elif isinstance(toml_item, items.Whitespace):
        toml_type = 'whitespace'
    elif isinstance(toml_item, items.AoT):
        toml_type = 'array-of-tables'
    elif isinstance(toml_item, items.Array):
        toml_type = 'array'
    else:
        toml_type = 'field'

    return toml_type


@dataclass(frozen=True)
class _ItemType:
    """"""
    item_type: Item
    parent_type: Optional[ParentItem]


@dataclass(frozen=True)
class CommentDescriptor:
    """"""
    comment: str
    line_no: int


@dataclass(frozen=True)
class Descriptor:
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
    tables: Optional[Set[Hierarchy]]


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


@dataclass(frozen=True)
class _StylingPosition:
    """"""
    item_type: StyleItem
    style: str
    line_no: int
    container: int


@dataclass
class _ArrayOfTablesPosition:
    """"""
    position: _ItemPosition
    tables: Dict[int, Dict[str, _TablePosition]]

    def update_tables(
        self, 
        array_position: int,
        hierarchy: str,
        table_position: _TablePosition
    ) -> None:
        """"""
        if array_position not in self.tables:
            self.tables.update({array_position: {hierarchy: table_position}})
        elif hierarchy not in self.tables[array_position]:
            self.tables[array_position].update({hierarchy: table_position})


@dataclass
class _StylingPositions:
    """"""
    comments: Dict[str, List[_StylingPosition]]
    whitespace: Dict[str, List[_StylingPosition]]

    def update_stylings(
        self, style_item: TOMLItem, position: _ItemPosition, line_no: int
    ) -> None:
        """"""
        style = cast(Union[items.Comment, items.Whitespace], style_item.item)

        if isinstance(style, items.Comment):
            styling = style.trivia.comment
            current_source = self.comments
        else:
            styling = style.value
            current_source = self.whitespace

        styling_position = _StylingPosition(
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
class _FieldPosition:
    """"""
    item_type: FieldItem
    line_no: int
    position: _ItemPosition
    value: Any
    comment: Optional[CommentDescriptor]
    styling: Optional[_StylingPositions]

    @classmethod
    def from_toml_item(cls, line_no: int, position: _ItemPosition, item: TOMLItem) -> _FieldPosition:
        """"""
        if isinstance(item.item, items.Array):
            styling = _StylingPositions(comments=dict(), whitespace=dict())
            comment_line_no = None
        else:
            styling = None
            comment_line_no = _TablePosition.find_comment_line_no(line_no=line_no, item=item.item)

        comment = _create_comment_descriptor(item=item.item, line_no=comment_line_no)
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
        comment_position = _TablePosition.find_comment_line_no(line_no=line_no, item=item.item)
        self.comment = comment_position


@dataclass(frozen=True)
class ContainerItem:
    """"""
    item_type: _ItemType
    key: Optional[str]
    hierarchy: str
    item: _Container

    @classmethod
    def from_toml_item(cls, item: TOMLItem) -> ContainerItem:
        """"""
        return cls(
            item_type=item.item_type,
            key=item.key,
            hierarchy=item.hierarchy,
            item=cast(_Container, item.item)
        )


@dataclass(frozen=True)
class TOMLItem:
    """"""
    item_type: _ItemType
    key: Optional[str]
    hierarchy: str
    item: items.Item

    @property
    def full_hierarchy(self) -> str:
        """"""
        return Hierarchy.create_hierarchy(hierarchy=self.hierarchy, update=self.key)

    @classmethod
    def from_parent_type(
        cls, key: str, hierarchy: str, toml_item: items.Item, parent_type: Optional[TomlType] = None
    ) -> TOMLItem:
        """"""
        item_type = _ItemType(
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

        item_type = _ItemType(
            item_type=get_item_type(toml_item=toml_item),
            parent_type=container.item_type.item_type
        )

        return cls(
            item_type=item_type, key=item_key, hierarchy=hierarchy, item=toml_item
        )


@dataclass
class _ItemPosition:
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
class _TablePosition:
    """"""
    item_type: TableItem
    parent_type: ParentItem
    line_no: int
    position: _ItemPosition
    comment: Optional[CommentDescriptor]
    styling: _StylingPositions
    fields: Dict[str, _FieldPosition]

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
        cls, line_no: int, position: _ItemPosition, container: ContainerItem
    ) -> _TablePosition:
        """"""
        comment_line_no = _TablePosition.find_comment_line_no(line_no=line_no, item=container.item)
        styling = _StylingPositions(comments=dict(), whitespace=dict())
        comment = _create_comment_descriptor(item=container.item, line_no=comment_line_no)
        return cls(
            line_no=line_no,
            item_type=cast(TableItem, container.item_type.item_type),
            parent_type=container.item_type.parent_type,
            comment=comment,
            position=copy.copy(position),
            styling=styling,
            fields=dict()
        )
        
    def add_field(self, item: TOMLItem, line_no: int, position: _ItemPosition) -> None:
        """"""
        field_position = _FieldPosition.from_toml_item(line_no=line_no, position=position, item=item)
        self.fields.update({item.key: field_position})


_WHITESPACE_PATTERN = r'^[ \n\r]*$'


class TOMLDocumentDescriptor:
    """"""
    def __init__(
        self,
        toml_source: Union[TOMLDocument, items.Table, items.AoT],
        hierarchy: Optional[str] = None
    ):
        self._current_line_number = 0

        # Line mappings for attributes occurring in document but outside of tables
        self._document_lines: Dict[str, _FieldPosition] = dict()
        self._document_stylings: _StylingPositions = _StylingPositions(
            comments=dict(), whitespace=dict()
        )

        # Line mappings for any array of tables objects
        self._array_of_tables: Dict[str, _ArrayOfTablesPosition] = dict()

        # Line mappings for attributes occurring within at least one table
        self._attribute_lines: Dict[str, _TablePosition] = dict()

        # Auto-management of positions of tables within an array of tables
        self._array_of_tables_positions: Dict[str, int] = dict()

        active_hierarchy = hierarchy or ''
        position = _ItemPosition(attribute=1, container=1)
        if isinstance(toml_source, items.AoT):
            self._generate_descriptor_from_array_of_tables(
                hierarchy=active_hierarchy, array=toml_source, position=position
            )          
        else:
            if isinstance(toml_source, items.Table):
                update_key = toml_source.name
            else:
                update_key = ''

            self._generate_descriptor_bridge(
                item=TOMLItem.from_parent_type(key=update_key, hierarchy=hierarchy, toml_item=toml_source),
                position=position
            )

    @property
    def number_of_tables(self) -> int:
        """"""

    @property
    def number_of_inline_tables(self) -> int:
        """"""

    @property
    def number_of_attributes(self) -> int:
        """"""

    @property
    def number_of_arrays(self) -> int:
        """"""

    @property
    def number_of_comments(self) -> int:
        """"""

    @property
    def number_of_fields(self) -> int:
        """"""

    @overload
    def get_attribute_from_aot(
        self, hierarchy: str, position: int, field: str
    ) -> FieldDescriptor:
        ...

    @overload
    def get_attribute_from_aot(
        self, hierarchy: str, position: int, field: None
    ) -> TableDescriptor:
        ...

    def get_attribute_from_aot(
        self, hierarchy: str, position: int, field: Optional[str] = None
    ) -> Union[FieldDescriptor, TableDescriptor]:
        """"""
        hierarchy_obj = Hierarchy.from_str_hierarchy(
            hierarchy=Hierarchy.create_hierarchy(hierarchy=hierarchy, update=field or '')
        )

        array_hierarchy: Optional[str] = self._get_array_hierarchy(hierarchy=hierarchy_obj)

        if array_hierarchy is None:
            raise InvalidArrayOfTablesError(
                "Hierarchy is not associated with an existing array of tables"
            )

        array_of_tables = self._array_of_tables[array_hierarchy]

        if position not in array_of_tables:
            raise InvalidArrayOfTablesError("Position is greater than the length of the array")

        position_hierarchies = array_of_tables.tables[position]

        if hierarchy not in position_hierarchies:
            raise InvalidHierarchyError("Hierarchy does not exist in set of valid hierarchies")

        table_position: _TablePosition = position_hierarchies[hierarchy]
        if field is not None:
            hierarchy_fields = table_position.fields
            if field not in hierarchy_fields:
                raise InvalidFieldError(
                    "Field does not exist in set of valid fields for the given hierarchy"
                )
            
            field_position: _FieldPosition = hierarchy_fields[field]
            return _create_field_descriptor(
                field=field,
                hierarchy=hierarchy_obj,
                field_position=field_position,
                parent_type=table_position.item_type,
                from_aot=True
            )
        else:
            tables = _find_nested_tables(
                root_hierarchy=array_hierarchy, hierarchies=position_hierarchies
            )
            return _create_table_descriptor(
                hierarchy=hierarchy_obj, table_position=table_position, tables=tables, from_aot=True
            )
        
    @overload
    def get_attribute(self, hierarchy: str, field: str) -> FieldDescriptor:
        ...

    @overload
    def get_attribute(self, hierarchy: Optional[str], field: str) -> FieldDescriptor:
        ...

    @overload
    def get_attribute(self, hierarchy: str, field: Optional[str]) -> TableDescriptor:
        ...

    def get_attribute(
        self, hierarchy: Optional[str] = None, field: Optional[str] = None
    ) -> Union[FieldDescriptor, TableDescriptor]:
        """"""
        if hierarchy is None and field is None:
            raise TypeError("Both the hierarchy and field arguments cannot be None")

        hierarchy_obj = Hierarchy.from_str_hierarchy(
            hierarchy=Hierarchy.create_hierarchy(hierarchy=hierarchy or '', update=field or '')
        )

        if hierarchy is None:
            if field not in self._document_lines:
                raise InvalidFieldError("Field does not exist in top-level document space")
            
            field_position: _FieldPosition = self._document_lines[field]
            return _create_field_descriptor(
                field=field,
                hierarchy=hierarchy_obj,
                field_position=field_position,
                parent_type='document',
                from_aot=False
            )

        else:
            if hierarchy not in self._attribute_lines:
                raise InvalidHierarchyError("Hierarchy does not exist in set of valid hierarchies")
            
            table_position: _TablePosition = self._attribute_lines[hierarchy]
            if field is not None:
                if field not in table_position.fields:
                    raise InvalidFieldError(
                        "Field does not exist in set of valid attributes for the given hierarchy"
                    )
                
                field_position: _FieldPosition = table_position.fields[field]
                return _create_field_descriptor(
                    field=field,
                    hierarchy=hierarchy_obj,
                    field_position=field_position,
                    parent_type=table_position.parent_type,
                    from_aot=False
                )
            else:
                tables = _find_nested_tables(
                    root_hierarchy=hierarchy, hierarchies=self._attribute_lines
                )
                return _create_table_descriptor(
                    hierarchy=hierarchy_obj, table_position=table_position, tables=tables, from_aot=False
                )

    @overload
    def get_styling(
        self, styling: str, position: None, hierarchy: Optional[str] = None
    ) -> List[StyleDescriptor]:
        ...
        
    @overload
    def get_styling(
        self, styling: str, position: int, hierarchy: Optional[str] = None
    ) -> StyleDescriptor:
        ...

    def get_styling(
        self, styling: str, position: Optional[int] = None, hierarchy: Optional[str] = None
    ) -> Union[StyleDescriptor, List[StyleDescriptor]]:
        """"""
        hierarchy_obj: Optional[Hierarchy] = (
            Hierarchy.from_str_hierarchy(hierarchy=hierarchy) if hierarchy is not None else None
        )

        is_comment = not re.match(_WHITESPACE_PATTERN, styling)
        stylings: _StylingPositions
        parent_type: ParentItem

        if hierarchy is None:
            parent_type = 'document'
            stylings = self._document_stylings
        else:
            if hierarchy not in self._attribute_lines:
                raise InvalidHierarchyError("Hierarchy does not exist in set of valid hierarchies")
            
            table_position: _TablePosition = self._attribute_lines[hierarchy]
            parent_type = table_position.item_type
            stylings = table_position.styling

        styling_space = stylings.comments if is_comment else stylings.whitespace
        if styling not in styling_space:
            raise InvalidStylingError("Styling does not exist in set of valid stylings")
        
        line_nos = styling_space[styling]

        if position is not None:
            styling_position: _StylingPosition = line_nos[position]

            return _create_style_descriptor(
                styling_position=styling_position, hierarchy=hierarchy_obj, parent_type=parent_type
            )
        else:
            return [
                _create_style_descriptor(
                    styling_position=styling_position, hierarchy=hierarchy_obj, parent_type=parent_type
                )
                for styling_position in line_nos
            ]

    def _get_array_hierarchy(self, hierarchy: Union[str, Hierarchy]) -> Optional[str]:
        """"""
        if isinstance(hierarchy, Hierarchy):
            hierarchy_obj = hierarchy
        else:
            hierarchy_obj = Hierarchy.from_str_hierarchy(hierarchy=hierarchy)
        
        return hierarchy_obj.shortest_sub_hierarchy(
            hierarchies=list(self._array_of_tables.keys())
        )

    def _get_aot_table(self, hierarchy: str) -> _TablePosition:
        """"""
        array_hierarchy: Optional[str] = self._get_array_hierarchy(hierarchy=hierarchy)

        array_position = self._array_of_tables_positions[hierarchy]
        table_position = self._array_of_tables[array_hierarchy].tables[array_position][hierarchy]

        return table_position

    def _update_styling(
        self, container: TOMLItem, style: TOMLItem, position: _ItemPosition, is_aot: bool
    ) -> None:
        """"""
        styling_positions: _StylingPositions

        if isinstance(container.item, TOMLDocument):
            styling_positions = self._document_stylings
        elif is_aot:
            table_position = self._get_aot_table(hierarchy=style.hierarchy)
            if isinstance(container.item, (items.Table, items.InlineTable)):
                styling_positions = table_position.styling
            else:
                styling_positions = table_position.fields[container.key].styling
        elif isinstance(container.item, (items.Table, items.InlineTable, OutOfOrderTableProxy)):
            styling_positions = self._attribute_lines[style.hierarchy].styling
        else:
            if not container.hierarchy:
                styling_positions = self._document_lines[container.key].styling
            else:
                styling_positions = self._attribute_lines[style.hierarchy].fields[container.key].styling

        styling_positions.update_stylings(
            style_item=style, position=position, line_no=self._current_line_number
        )

    def _update_attribute(self, item: TOMLItem, position: _ItemPosition) -> None:
        """"""
        self._attribute_lines[item.hierarchy].add_field(
            item=item, line_no=self._current_line_number, position=position
        )

    def _update_document(self, item: TOMLItem, position: _ItemPosition) -> None:
        """"""
        self._document_lines[item.key] = _FieldPosition.from_toml_item(
            line_no=self._current_line_number, position=position, item=item
        )

    def _update_array_of_tables(self, item: TOMLItem, position: _ItemPosition) -> None:
        """"""
        array_hierarchy: Optional[str] = self._get_array_hierarchy(hierarchy=item.hierarchy)
        array_position = self._array_of_tables_positions[item.hierarchy]
    
        self._array_of_tables[array_hierarchy].tables[array_position][item.hierarchy].add_field(
            item=item, line_no=self._current_line_number, position=position
        )

    def _add_table_to_attributes(
        self, hierarchy: str, position: _ItemPosition, container: ContainerItem
    ) -> None:
        """"""
        table_position = _TablePosition.from_table_item(
            line_no=self._current_line_number, position=position, container=container
        )
        self._attribute_lines.update({hierarchy: table_position})

    def _add_table_to_array_of_tables(
        self, hierarchy: str, position: _ItemPosition, container: ContainerItem
    ) -> None:
        """"""
        array_hierarchy: Optional[str] = self._get_array_hierarchy(hierarchy=hierarchy)
        
        self._array_of_tables_positions[hierarchy] += 1
        array_position = self._array_of_tables_positions[hierarchy]
        array_positions = self._array_of_tables[array_hierarchy]

        table_position = _TablePosition.from_table_item(
            line_no=self._current_line_number, position=position, container=container
        )

        array_positions.update_tables(
            array_position=array_position, hierarchy=hierarchy, table_position=table_position
        )

    def _update_attribute_descriptor(
        self, item: TOMLItem, position: _ItemPosition, is_doc: bool, is_aot: bool
    ) -> None:
        """"""
        if is_doc:
            self._update_document(item=item, position=position)
        elif is_aot:
            self._update_array_of_tables(item=item, position=position)
        else:
            self._update_attribute(item=item, position=position)

    def _update_array_comment(self, item: TOMLItem, is_doc: bool, is_aot: bool) -> None:
        """"""
        field_position: _FieldPosition
        if is_doc:
            field_position = self._document_lines[item.key]
        elif is_aot:
            field_position = self._get_aot_table(hierarchy=item.hierarchy).fields[item.key]
        else:
            field_position = self._attribute_lines[item.hierarchy].fields[item.key]

        field_position.update_comment(item=item, line_no=self._current_line_number)

    def _generate_descriptor_from_array_of_tables(self, hierarchy: str, array: items.AoT, position: _ItemPosition) -> None:
        """"""
        self._array_of_tables_positions[hierarchy] = 0
        self._array_of_tables[hierarchy] = _ArrayOfTablesPosition(position=copy.copy(position), tables=dict())

        hierarchy_root = Hierarchy.remove_recent_table(hierarchy=hierarchy)

        for index, table in enumerate(array.body):
            table_position = index + 1
            table_item = TOMLItem.from_parent_type(
                key=table.name, hierarchy=hierarchy_root, item=table, parent_type='array-of-tables'
            )
            self._generate_descriptor_bridge(
                item=table_item,
                position=_ItemPosition(attribute=table_position, container=table_position),
                is_aot=True
            )

    def _generate_descriptor_bridge(self, item: TOMLItem, position: _ItemPosition, is_aot: bool = False) -> None:
        """"""
        self._generate_descriptor(
            container=ContainerItem.from_toml_item(item=item), position=position, is_aot=is_aot
        )

    def _generate_descriptor(self, container: ContainerItem, position: _ItemPosition, is_aot: bool = False) -> None:
        """"""
        is_doc = False
        new_position = _ItemPosition(attribute=1, container=1)

        if isinstance(container.item, items.Array):
            new_hierarchy = container.hierarchy
        else:
            new_hierarchy = Hierarchy.create_hierarchy(hierarchy=container.hierarchy, update=container.key)

        if not (isinstance(container.item, items.Table) and container.item.is_super_table()):
            if is_aot and isinstance(container.item, items.Table):
                self._add_table_to_array_of_tables(
                    hierarchy=new_hierarchy, position=position, container=container
                )
            elif not isinstance(container.item, (TOMLDocument, items.Array)):
                self._add_table_to_attributes(
                    hierarchy=new_hierarchy, position=position, container=container
                )

        table_body_items: List[Tuple[Optional[items.Key], items.Item]]

        # Since an inline table is contained only on a single line, and thus,
        # on the same line as the table header, the line number is intialized to 0
        if isinstance(container.item, (items.Table, items.InlineTable)):
            table_body_items = container.item.value.body
        elif isinstance(container.item, items.Array):
            table_body_items = _reorganize_array(array=container)
        elif isinstance(container.item, OutOfOrderTableProxy):
            table_body_items = container.item._container.body
        else:
            is_doc = True
            table_body_items = container.item.body

        if (
            isinstance(container.item, TOMLDocument) or
            (isinstance(container.item, items.Table) and not container.item.is_super_table())
        ):
            self._current_line_number += 1

        # Iterate through each item appearing in the body of the table/arrays,
        # unpack each item and process accordingly
        for toml_body_item in table_body_items:
            toml_item = TOMLItem.from_body_item(
                hierarchy=new_hierarchy, body_item=toml_body_item, container=container
            )

            # If an inline table or array is encountered, the function
            # is run recursively since both data types can contain styling
            if isinstance(toml_item.item, items.Array):
                self._update_attribute_descriptor(
                    item=toml_item, position=new_position, is_doc=is_doc, is_aot=is_aot
                )
                self._generate_descriptor_bridge(item=toml_item, position=new_position, is_aot=is_aot)
                self._update_array_comment(item=toml_item, is_doc=is_doc, is_aot=is_aot)

                self._current_line_number += 1
                new_position.update_positions()
            elif isinstance(toml_item.item, items.InlineTable):
                self._generate_descriptor_bridge(item=toml_item, position=new_position, is_aot=is_aot)

                self._current_line_number += 1
                new_position.update_positions()
            # If one of the two styling elements are encountered, then the
            # memory address of the instance is generated as the key
            elif isinstance(toml_item.item, (items.Comment, items.Whitespace)):
                number_of_newlines = toml_item.item.as_string().count('\n')
                self._update_styling(
                    container=container, style=toml_item, position=new_position, is_aot=is_aot
                )
                self._current_line_number += number_of_newlines

                new_position.update_body_position()
            # If the item is an array of tables
            elif isinstance(toml_item.item, items.AoT):
                self._generate_descriptor_from_array_of_tables(
                    hierarchy=toml_item.full_hierarchy, array=toml_item.item, position=new_position
                )
                new_position.update_positions()
            # If a item instance is encountered that links to a field
            # (i.e. not a table or a field  in an array), then the attribute
            # mapping is updated
            elif isinstance(toml_item.item, (items.Table, OutOfOrderTableProxy)):
                self._generate_descriptor_bridge(item=toml_item, position=new_position, is_aot=is_aot)
                new_position.update_positions()
            else:
                if not isinstance(container.item, items.Array):
                    self._update_attribute_descriptor(
                        item=toml_item, position=new_position, is_doc=is_doc, is_aot=is_aot
                    )

                    if not isinstance(container.item, items.InlineTable):
                        self._current_line_number += 1
                new_position.update_positions()
