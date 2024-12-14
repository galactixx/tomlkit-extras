from dataclasses import dataclass
from typing import (
    Any,
    Optional
)

import pytest
from tomlkit import TOMLDocument
from tomlkit_extras import (
    create_inline_table,
    get_attribute_from_toml_source,
    InvalidHierarchyUpdateError,
    update_toml_source
)

from tests.typing import FixtureFunction

@dataclass(frozen=True)
class UpdateTestCase:
    """Dataclass representing a test case for the `update_toml_source` function"""
    fixture: FixtureFunction
    hierarchy: str
    update: Any
    full: bool = True
    _value: Optional[Any] = None

    @property
    def hierarchy_value(self) -> Any:
        if self._value is None:
            return self.update
        else:
            return self._value


@dataclass(frozen=True)
class InvalidUpdateTestCase:
    """
    Dataclass representing a test case for the error handling of the
    `update_toml_source` function.
    """
    fixture: FixtureFunction
    hierarchy: str
    update: Any
    error: str


@pytest.mark.parametrize(
    'test_case',
    [
        UpdateTestCase(
            'load_toml_a', 'project.name', 'Example Project New'
        ),
        UpdateTestCase(
            'load_toml_a',
            'members',
            {'name': "Jack"},
            False,
            [
                {'name': 'Alice', 'roles': [{'role': 'Developer'}, {'role': 'Designer'}]},
                {'name': 'Bob', 'roles': [{'role': 'Manager'}]},
                {'name': 'Jack'}
            ]
        ),
        UpdateTestCase(
            'load_toml_b', 'project', 'Example Project New'
        ),
        UpdateTestCase(
            'load_toml_b',
            'tool.ruff.lint.pydocstyle',
            create_inline_table(fields={'select': ["D102"], 'convention': ["numpy"]})
        ),
        UpdateTestCase('load_toml_c', 'tool.ruff.line-length', 90),
        UpdateTestCase('load_toml_c', 'tool.rye.managed', False)
    ]
)
def test_update_toml_document(
    test_case: UpdateTestCase, request: pytest.FixtureRequest
) -> None:
    """Function to test the functionality of `update_toml_source`."""
    toml_document: TOMLDocument = request.getfixturevalue(test_case.fixture)
    update_toml_source(
        hierarchy=test_case.hierarchy,
        toml_source=toml_document,
        update=test_case.update,
        full=test_case.full
    )
    toml_structure = get_attribute_from_toml_source(
        hierarchy=test_case.hierarchy, toml_source=toml_document
    )
    assert toml_structure == test_case.hierarchy_value


@pytest.mark.parametrize(
    'test_case',
    [
        InvalidUpdateTestCase(
            'load_toml_a',
            'members.roles',
            {'role': "Analyst"},
            'Hierarchy maps to multiple items within an array of tables, not a feature of this function'
        ),
        InvalidUpdateTestCase(
            'load_toml_c',
            'tool.poetry',
            {'name': "tomlkit-extras"},
            'Hierarchy specified does not exist in TOMLDocument instance'
        )
    ]
)
def test_update_toml_document_errors(
    test_case: InvalidUpdateTestCase, request: pytest.FixtureRequest
) -> None:
    """Function to test the error handling of `update_toml_source`."""
    toml_document: TOMLDocument = request.getfixturevalue(test_case.fixture)
    with pytest.raises(InvalidHierarchyUpdateError) as exc_info:
        update_toml_source(
            hierarchy=test_case.hierarchy, toml_source=toml_document, update=test_case.update
        )

    assert exc_info.value.message == test_case.error
