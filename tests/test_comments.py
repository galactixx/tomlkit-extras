from typing import List

from tomlkit import items, TOMLDocument
from tomlkit_extensions import (
    get_attribute_from_toml_source,
    get_array_field_comment,
    get_comments,
    Hierarchy,
    load_toml_file,
    StructureComment
)

def test_comments_toml_a() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_a.toml')


def test_comments_toml_b() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_b.toml')


def test_comments_toml_c() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_c.toml')

    # Retrieve all comments from the top-level document space
    document_comments: List[StructureComment] = get_comments(toml_source=toml_document)
    assert document_comments == [
        StructureComment(hierarchy=None, line_no=1, comment='# this is a document comment')
    ]

    # Retrieve all table comments from the tool.ruff.lint table
    HIERARCHY_RUFF_LINT = Hierarchy.from_str_hierarchy(hierarchy='tool.ruff.lint')

    ruff_lint_comments: List[StructureComment] = get_comments(
        toml_source=toml_document, hierarchy=HIERARCHY_RUFF_LINT
    )
    assert ruff_lint_comments == [
        StructureComment(hierarchy=HIERARCHY_RUFF_LINT, line_no=3, comment='# this is the first comment for lint table')
    ]

    # Retrieve all table comments from the tool.ruff table
    HIERARCHY_RUFF = Hierarchy.from_str_hierarchy(hierarchy='tool.ruff')

    ruff_comments: List[StructureComment] = get_comments(toml_source=toml_document, hierarchy=HIERARCHY_RUFF)
    assert ruff_comments == [
        StructureComment(hierarchy=HIERARCHY_RUFF, line_no=2, comment='# this is a tool.ruff comment')
    ]

    # Grab all array comments
    dev_dependencies_array: items.Array = get_attribute_from_toml_source(
        hierarchy='tool.rye.dev-dependencies', toml_source=toml_document
    )

    ruff_comment = get_array_field_comment(array=dev_dependencies_array, array_item='ruff>=0.4.4')
    assert ruff_comment == '# ruff version'

    ruff_comment = get_array_field_comment(array=dev_dependencies_array, array_item='mypy>=0.812')
    assert ruff_comment is None

    ruff_comment = get_array_field_comment(array=dev_dependencies_array, array_item='sphinx>=3.5')
    assert ruff_comment == '# sphinx version'

    ruff_comment = get_array_field_comment(array=dev_dependencies_array, array_item='setuptools>=56.0')
    assert ruff_comment == '# setuptools version'