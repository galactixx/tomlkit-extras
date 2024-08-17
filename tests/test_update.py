from typing import Any
import copy

import pytest
import tomlkit
from tomlkit import TOMLDocument
from tomlkit_extras import (
    get_attribute_from_toml_source,
    InvalidHierarchyError,
    load_toml_file,
    update_toml_source
)

def _update_and_assertion_test(
    hierarchy: str, update: Any, toml_document: TOMLDocument
) -> None:
    """"""
    update_toml_source(
        hierarchy=hierarchy, toml_source=toml_document, update=update
    )
    assert get_attribute_from_toml_source(
        hierarchy=hierarchy, toml_source=toml_document
    ) == update


def test_update_toml_a() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_a.toml')

    # Update the project.name hierarchy
    _update_and_assertion_test(
        hierarchy='project.name', update='Example Project New', toml_document=toml_document
    )

    # Update the members hierarchy
    update_toml_source(
        hierarchy='members', toml_source=toml_document, update={'name': "Jack"}, full=False
    )
    members = get_attribute_from_toml_source(
        hierarchy='members', toml_source=toml_document
    )
    assert isinstance(members, list)
    assert members == [
        {'name': 'Alice', 'roles': [{'role': 'Developer'}, {'role': 'Designer'}]},
        {'name': 'Bob', 'roles': [{'role': 'Manager'}]},
        {'name': 'Jack'}
    ]

    # Try to update the members.roles hierarchy, which will result in an error
    with pytest.raises(InvalidHierarchyError) as exc_info:
        update_toml_source(
            hierarchy='members.roles', toml_source=toml_document, update={'role': "Analyst"}
        )
    assert str(exc_info.value) == (
        'Hierarchy maps to multiple items within an array of tables, not a feature of this function'
    )


def test_update_toml_b() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_b.toml')

    # Update the project hierarchy
    _update_and_assertion_test(
        hierarchy='project', update='Example Project New', toml_document=toml_document
    )

    # Update the tool.ruff.lint.pydocstyle hierarchy
    inline_table = tomlkit.inline_table()
    inline_table.update({'select': ["D102"]})
    update_toml_source(
        hierarchy='tool.ruff.lint.pydocstyle', toml_source=toml_document, update=inline_table
    )
    lint_pydocstyle = get_attribute_from_toml_source(
        hierarchy='tool.ruff.lint.pydocstyle', toml_source=toml_document
    )
    assert not isinstance(lint_pydocstyle, list)
    assert lint_pydocstyle.unwrap() == inline_table.unwrap()

    inline_table_new = copy.deepcopy(inline_table)
    inline_table_new.update({'convention': ["numpy"]})
    update_toml_source(
        hierarchy='tool.ruff.lint.pydocstyle', toml_source=toml_document, update=inline_table_new, full=False
    )
    lint_pydocstyle_updated = get_attribute_from_toml_source(
        hierarchy='tool.ruff.lint.pydocstyle', toml_source=toml_document
    )
    assert not isinstance(lint_pydocstyle_updated, list)
    assert lint_pydocstyle_updated.unwrap() == inline_table_new.unwrap()


def test_update_toml_c() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_c.toml')

    # Update the tool.ruff.line-length hierarchy
    _update_and_assertion_test(
        hierarchy='tool.ruff.line-length', update=90, toml_document=toml_document
    )

    # Update the tool.rye.managed hierarchy
    _update_and_assertion_test(
        hierarchy='tool.rye.managed', update=False, toml_document=toml_document
    )

    # Try to update a hierarchy that does not exist
    with pytest.raises(InvalidHierarchyError) as exc_info:
        update_toml_source(
            hierarchy='tool.poetry', toml_source=toml_document, update={'name': "tomlkit-extras"}
        )
    assert str(exc_info.value) == (
        'Hierarchy specified does not exist in TOMLDocument instance'
    )