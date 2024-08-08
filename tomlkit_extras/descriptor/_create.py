from __future__ import annotations
from typing import (
    Optional,
    Set,
    TYPE_CHECKING
)

from tomlkit import items

from tomlkit_extras._typing import ParentItem
from tomlkit_extras._hierarchy import Hierarchy
from tomlkit_extras.descriptor._descriptors import (
    CommentDescriptor,
    FieldDescriptor,
    StyleDescriptor,
    TableDescriptor
)

if TYPE_CHECKING:
    from tomlkit_extras.descriptor._types import (
        FieldPosition,
        StylingPosition,
        TablePosition
    )

def create_comment_descriptor(item: items.Item, line_no: Optional[int]) -> Optional[CommentDescriptor]:
    """"""
    return (
        CommentDescriptor(comment=item.trivia.comment, line_no=line_no)
        if line_no is not None else None
    )


def create_style_descriptor(
    styling_position: 'StylingPosition', hierarchy: Optional[Hierarchy], parent_type: ParentItem
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


def create_field_descriptor(
    field: str,
    hierarchy: Hierarchy,
    field_position: 'FieldPosition',
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


def create_table_descriptor(
    hierarchy: Hierarchy, table_position: 'TablePosition', tables: Set[Hierarchy], from_aot: bool
) -> TableDescriptor:
    """"""
    fields = {
        field: create_field_descriptor(
            field=field,
            hierarchy=Hierarchy(hierarchy=hierarchy.full_hierarchy, attribute=field),
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
        child_tables=tables or None
    )