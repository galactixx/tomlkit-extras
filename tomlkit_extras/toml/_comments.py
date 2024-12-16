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
    AnnotatedContainer,
    BodyContainerItem,
    ContainerComment,
    TOMLHierarchy
)

def _container_has_comments(attribute: Union[TOMLDocument, items.Item]) -> bool:
    """
    Private function to determine if a specific tomlkit type can contain
    annotations.
    """
    return isinstance(attribute, (TOMLDocument, items.Table, items.AoT, items.Array))


def get_comments(
    toml_source: AnnotatedContainer, hierarchy: Optional[TOMLHierarchy] = None
) -> Optional[List[ContainerComment]]:
    """
    Retrieves and returns all comments appearing in the top-level space of a given
    tomklit type. A TOML source of type `AnnotatedContainer` must be passed in.
    
    If no heirarchy is specified then the search will occur in the TOML source
    passed. Otherwise if a hierarchy is included, then it must be relative to
    the source. The item located at the hierarchy will be retrieved and the
    search will occur within that item.

    Returns a tuple where the first item is the line number where the comment
    is located and the second item is the comment itself.

    Will return None if no comments were found.

    Args:
        toml_source (`AnnotatedContainer`): An `AnnotatedContainer` instance.
        hierarchy (`TOMLHierarchy` | None): None or a `TOMLHierarchy` instance.

    Returns:
        List[`ContainerComment`] | None: None if no comments were found, or a list of
            `ContainerComment` instances.
    """
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
            raise ValueError("Attribute is not a structure that can contain comments")

        attributes = cast(
            List[Union[TOMLDocument, items.Table, items.Array]],
            attribute
        )

    comments: List[ContainerComment] = []
    for attr in attributes:
        document_descriptor = TOMLDocumentDescriptor(toml_source=attr, top_level_only=True)

        for comment_descriptor in document_descriptor.get_top_level_stylings(styling='comment'):
            comments.append((comment_descriptor.line_no, comment_descriptor.style))

    return comments if comments else None


def get_array_field_comment(array: items.Array, array_item: Any) -> Optional[str]:
    """
    Will return the comment associated with an array item appearing within a
    `tomlkit.items.Array` instance. Association in this case means the first comment
    appearing after the item in question, but before any whitespace (a new line).

    Will return None if no comment was found.
    
    Args:
        array (`tomlkit.items.Array`): A `tomlkit.items.Array` instance.
        array_item (Any): Any type corresponding to an array item.
    
    Returns:
        str | None: None if no comment was found, or a string comment if found.
    """
    array_items = get_container_body(toml_source=array)
    array_items_iter: Iterator[BodyContainerItem] = iter(array_items)

    seen_first_ws_after_comment = False
    seen_array_item = False
    array_item_comment: Optional[str] = None

    try:
        while (
            not (seen_array_item and seen_first_ws_after_comment) and
            array_item_comment is None
        ):
            _, array_body_item = decompose_body_item(body_item=next(array_items_iter))

            if not seen_array_item:
                seen_array_item = array_body_item == array_item
            elif isinstance(array_body_item, items.Whitespace):
                seen_first_ws_after_comment = '\n' in array_body_item.value
            elif isinstance(array_body_item, items.Comment):
                array_item_comment = array_body_item.trivia.comment
    except StopIteration:
        pass

    if not seen_array_item:
        raise InvalidArrayItemError(
            "Data item does not exist in specified array",
            array_items
        )

    return array_item_comment