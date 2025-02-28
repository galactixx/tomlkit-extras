from dataclasses import dataclass
from typing import List, Optional, cast

import pytest
from tomlkit import TOMLDocument, items

from tests.typing import FixtureFunction
from tomlkit_extras import (
    get_array_field_comment,
    get_attribute_from_toml_source,
    get_comments,
)
from tomlkit_extras._typing import ContainerComment


@pytest.fixture(scope="function")
def load_c_dev_field_array(load_toml_c: TOMLDocument) -> items.Array:
    """
    Function-scoped fixture for the toml_c tool.rye.dev-dependencies
    `items.Array` instance. Used to test the `get_array_field_comment`
    function.
    """
    dev_dependencies_array = get_attribute_from_toml_source(
        hierarchy="tool.rye.dev-dependencies", toml_source=load_toml_c
    )
    dev_dependencies_array = cast(items.Array, dev_dependencies_array)
    return dev_dependencies_array


@dataclass(frozen=True)
class CommentsTestCase:
    """Dataclass representing a test case for the `get_comments` function."""

    fixture: FixtureFunction
    hierarchy: Optional[str]
    comments: Optional[List[ContainerComment]]


@dataclass(frozen=True)
class ArrayCommentTestCase:
    """
    Dataclass representing a test case for the `get_array_field_comment`
    function.
    """

    item: str
    comment: Optional[str]


@pytest.mark.parametrize(
    "test_case",
    [
        CommentsTestCase("load_toml_a", None, [(1, "# this is a document comment")]),
        CommentsTestCase("load_toml_a", "project", None),
        CommentsTestCase("load_toml_a", "details", None),
        CommentsTestCase("load_toml_a", "members", None),
        CommentsTestCase("load_toml_b", None, [(4, "# this is a document comment")]),
        CommentsTestCase(
            "load_toml_b",
            "tool.ruff.lint",
            [
                (1, "# this is the first comment for lint table"),
                (2, "# this is the second comment for lint table"),
            ],
        ),
        CommentsTestCase("load_toml_b", "main_table", None),
        CommentsTestCase("load_toml_c", None, [(1, "# this is a document comment")]),
        CommentsTestCase(
            "load_toml_c",
            "tool.ruff.lint",
            [(3, "# this is the first comment for lint table")],
        ),
        CommentsTestCase(
            "load_toml_c", "tool.ruff", [(2, "# this is a tool.ruff comment")]
        ),
        CommentsTestCase("load_toml_c", "tool.rye", None),
    ],
)
def test_comments_from_toml_document(
    test_case: CommentsTestCase, request: pytest.FixtureRequest
) -> None:
    """Function to test the functionality of `get_comments`."""
    toml_document: TOMLDocument = request.getfixturevalue(test_case.fixture)
    comments = get_comments(toml_source=toml_document, hierarchy=test_case.hierarchy)
    assert test_case.comments == comments


@pytest.mark.parametrize(
    "test_case",
    [
        ArrayCommentTestCase(item="ruff>=0.4.4", comment="# ruff version"),
        ArrayCommentTestCase(item="mypy>=0.812", comment=None),
        ArrayCommentTestCase(item="sphinx>=3.5", comment="# sphinx version"),
        ArrayCommentTestCase(item="setuptools>=56.0", comment="# setuptools version"),
    ],
)
def test_array_comments_toml_c(
    test_case: ArrayCommentTestCase, load_c_dev_field_array: items.Array
) -> None:
    """Function to test the functionality of `get_array_field_comment`."""
    ruff_comment = get_array_field_comment(
        array=load_c_dev_field_array, array_item=test_case.item
    )
    assert test_case.comment == ruff_comment
