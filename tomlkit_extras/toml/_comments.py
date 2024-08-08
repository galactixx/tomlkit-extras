from dataclasses import dataclass
from typing import (
    Any,
    List,
    Optional
)

from tomlkit import items, TOMLDocument
from tomlkit.container import OutOfOrderTableProxy

from tomlkit_extras._exceptions import InvalidArrayItemError
from tomlkit_extras._hierarchy import Hierarchy
from tomlkit_extras.descriptor._descriptor import TOMLDocumentDescriptor
from tomlkit_extras._typing import ContainerLike, TOMLHierarchy
from tomlkit_extras.toml._retrieval import get_attribute_from_toml_source
from tomlkit_extras._utils import (
    decompose_body_item,
    get_container_body,
    standardize_hierarchy
)

@dataclass(frozen=True)
class StructureComment:
    """"""
    hierarchy: Optional[Hierarchy]
    line_no: int
    comment: str


def get_comments(
    toml_source: ContainerLike, hierarchy: Optional[TOMLHierarchy] = None
) -> Optional[List[StructureComment]]:
    """"""
    if hierarchy is None:
        attribute = toml_source
    else:
        attribute = get_attribute_from_toml_source(hierarchy=hierarchy, toml_source=toml_source)
    
    if (
        isinstance(attribute, list) or
        not isinstance(attribute, (TOMLDocument, items.Table, OutOfOrderTableProxy, items.Array))
    ):
        return None
    else:
        hierarchy_obj: Hierarchy = standardize_hierarchy(hierarchy=hierarchy)
        comments: List[StructureComment] = []

        document_descriptor = TOMLDocumentDescriptor(toml_source=attribute, top_level_only=True)

        for comment_descriptor in document_descriptor.get_top_level_stylings(styling='comment'):
            comments.append(
                StructureComment(
                    hierarchy=hierarchy_obj, line_no=comment_descriptor.line_no, comment=comment_descriptor.style
                )
            )

        return comments if comments else None


def get_array_field_comment(array: items.Array, array_item: Any) -> Optional[str]:
    """"""
    array_body_items = iter(get_container_body(toml_source=array))

    seen_first_ws_after_comment = False
    seen_array_item = False
    array_item_comment: Optional[str] = None

    try:
        while (
            not (seen_array_item and seen_first_ws_after_comment) and
            array_item_comment is None
        ):
            _, array_body_item = decompose_body_item(body_item=next(array_body_items))

            if not seen_array_item:
                seen_array_item = array_body_item == array_item
            else:
                if isinstance(array_body_item, items.Whitespace):
                    seen_first_ws_after_comment = '\n' in array_body_item.value
                elif isinstance(array_body_item, items.Comment):
                    array_item_comment = array_body_item.trivia.comment
    except StopIteration:
        pass

    if not seen_array_item:
        raise InvalidArrayItemError("Data item does not exist in specified array")

    return array_item_comment