from dataclasses import dataclass
from typing import (
    cast,
    List,
    Optional
)

import pytest
from tomlkit import items, TOMLDocument
from tomlkit_extras import (
    get_comments,
    get_array_field_comment,
    get_attribute_from_toml_source
)

from tomlkit_extras._typing import ContainerComment

@pytest.fixture(scope='module')
def load_c_dev_field_array(load_toml_c: TOMLDocument) -> items.Array:
    """"""
    dev_dependencies_array = get_attribute_from_toml_source(
        hierarchy='tool.rye.dev-dependencies', toml_source=load_toml_c
    )
    dev_dependencies_array = cast(items.Array, dev_dependencies_array)
    return dev_dependencies_array


@dataclass(frozen=True)
class CommentsTestCase:
    """"""
    hierarchy: str
    comments: Optional[List[ContainerComment]]


@dataclass(frozen=True)
class ArrayCommentTestCase:
    """"""
    item: str
    comment: Optional[str]


@pytest.mark.parametrize(
    'test_case',
    [
        CommentsTestCase(
            hierarchy=None, comments=[(1, 1, '# this is a document comment')]
        ),
        CommentsTestCase(
            hierarchy='project', comments=None
        ),
        CommentsTestCase(
            hierarchy='details', comments=None
        ),
        CommentsTestCase(
            hierarchy='members', comments=None
        )
    ]
)
def test_comments_toml_a(test_case: CommentsTestCase, load_toml_a: TOMLDocument) -> None:
    """"""
    comments = get_comments(toml_source=load_toml_a, hierarchy=test_case.hierarchy)
    assert test_case.comments == comments


@pytest.mark.parametrize(
    'test_case',
    [
        CommentsTestCase(
            hierarchy=None, comments=[(1, 4, '# this is a document comment')]
        ),
        CommentsTestCase(
            hierarchy='tool.ruff.lint',
            comments=[
                (1, 1, '# this is the first comment for lint table'),
                (1, 2, '# this is the second comment for lint table')
            ]
        ),
        CommentsTestCase(
            hierarchy='main_table', comments=None
        )
    ]
)
def test_comments_toml_b(test_case: CommentsTestCase, load_toml_b: TOMLDocument) -> None:
    """"""
    comments = get_comments(toml_source=load_toml_b, hierarchy=test_case.hierarchy)
    assert test_case.comments == comments


@pytest.mark.parametrize(
    'test_case',
    [
        CommentsTestCase(
            hierarchy=None,
            comments=[(1, 1, '# this is a document comment')]
        ),
        CommentsTestCase(
            hierarchy='tool.ruff.lint',
            comments=[(1, 3, '# this is the first comment for lint table')]
        ),
        CommentsTestCase(
            hierarchy='tool.ruff',
            comments=[(1, 2, '# this is a tool.ruff comment')]
        ),
        CommentsTestCase(
            hierarchy='tool.rye', comments=None
        )
    ]
)
def test_comments_toml_c(test_case: CommentsTestCase, load_toml_c: TOMLDocument) -> None:
    """"""
    comments = get_comments(toml_source=load_toml_c, hierarchy=test_case.hierarchy)
    assert test_case.comments == comments


@pytest.mark.parametrize(
    'test_case',
    [
        ArrayCommentTestCase(item='ruff>=0.4.4', comment='# ruff version'),
        ArrayCommentTestCase(item='mypy>=0.812', comment=None),
        ArrayCommentTestCase(item='sphinx>=3.5', comment='# sphinx version'),
        ArrayCommentTestCase(item='setuptools>=56.0', comment='# setuptools version')
    ]
)
def test_array_comments_toml_c(
    test_case: ArrayCommentTestCase, load_c_dev_field_array: items.Array
) -> None:
    """"""
    ruff_comment = get_array_field_comment(array=load_c_dev_field_array, array_item=test_case.item)
    assert test_case.comment == ruff_comment