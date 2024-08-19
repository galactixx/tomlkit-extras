from typing import (
    Any,
    cast,
    Iterator,
    List,
    Optional,
    Union
)

from tomlkit import items, TOMLDocument
from tomlkit.container import OutOfOrderTableProxy

from tomlkit_extras.toml._out_of_order import fix_out_of_order_table
from tomlkit_extras._exceptions import InvalidArrayItemError
from tomlkit_extras.descriptor._descriptor import TOMLDocumentDescriptor
from tomlkit_extras.toml._retrieval import get_attribute_from_toml_source
from tomlkit_extras._utils import (
    decompose_body_item,
    get_container_body
)
from tomlkit_extras._typing import (
    ContainerBodyItem,
    ContainerComments, 
    HasComments, 
    TOMLHierarchy
)

def _container_has_comments(attribute: items.Item) -> bool:
    """"""
    return isinstance(attribute, (TOMLDocument, items.Table, items.AoT, items.Array))


def get_comments(
    toml_source: HasComments, hierarchy: Optional[TOMLHierarchy] = None
) -> Optional[List[ContainerComments]]:
    """"""
    if isinstance(toml_source, items.Array) or hierarchy is None:
        if isinstance(toml_source, OutOfOrderTableProxy):
            toml_source = fix_out_of_order_table(table=toml_source)

        attributes = [toml_source]
    else:
        attribute = get_attribute_from_toml_source(
            hierarchy=hierarchy, toml_source=toml_source, fix_order=True
        )
        if not isinstance(attribute, list) or isinstance(attribute, items.AoT):
            attribute = [attribute]

        if not all(_container_has_comments(attribute=attr) for attr in attribute):
            raise ValueError("Attribute is not a structures that can contain comments")

        attributes = cast(
            List[Union[TOMLDocument, items.Table, items.AoT, items.Array]],
            attribute
        )

    comments: List[ContainerComments] = []
    for attr_index, attr in enumerate(attributes):
        document_descriptor = TOMLDocumentDescriptor(toml_source=attr, top_level_only=True)

        for comment_descriptor in document_descriptor.get_top_level_stylings(styling='comment'):
            comments.append((attr_index + 1, comment_descriptor.line_no, comment_descriptor.style))

    return comments if comments else None


def get_array_field_comment(array: items.Array, array_item: Any) -> Optional[str]:
    """"""
    array_body_items: Iterator[ContainerBodyItem] = iter(get_container_body(toml_source=array))

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
            elif isinstance(array_body_item, items.Whitespace):
                seen_first_ws_after_comment = '\n' in array_body_item.value
            elif isinstance(array_body_item, items.Comment):
                array_item_comment = array_body_item.trivia.comment
    except StopIteration:
        pass

    if not seen_array_item:
        raise InvalidArrayItemError("Data item does not exist in specified array")

    return array_item_comment