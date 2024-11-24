from dataclasses import dataclass
from typing import (
    Any,
    Type
)

import pytest
from tomlkit import items, TOMLDocument
from tomlkit.container import OutOfOrderTableProxy
from tomlkit_extras import (
    get_attribute_from_toml_source,
    is_toml_instance
)

from tests.typing import FixtureFunction

@dataclass(frozen=True)
class RetrievalTestCase:
    """
    Dataclass representing a test case for the `get_attribute_from_toml_source`
    function.
    """
    fixture: FixtureFunction
    hierarchy: str
    value: Any
    value_type: Type[Any]


@pytest.mark.parametrize(
    'test_case',
    [
        RetrievalTestCase('load_toml_a', 'project.name', 'Example Project', str),
        RetrievalTestCase(
            'load_toml_a',
            'details.description',
            'A sample project configuration',
            str
        ),
        RetrievalTestCase('load_toml_a', 'members.name', ['Alice', 'Bob'], str),
        RetrievalTestCase(
            'load_toml_a',
            'members',
            [
                {
                    'name': 'Alice',
                    'roles': [{'role': 'Developer'}, {'role': 'Designer'}]
                },
                {
                    'name': 'Bob',
                    'roles': [{'role': 'Manager'}]
                }
            ],
            items.Table
        ),
        RetrievalTestCase(
            'load_toml_a',
            'members.roles',
            [
                [{'role': 'Developer'}, {'role': 'Designer'}],
                [{'role': 'Manager'}]
            ],
            items.AoT
        ),
        RetrievalTestCase(
            'load_toml_a',
            'members.roles.role',
            ['Developer', 'Designer', 'Manager'],
            str
        ),
        RetrievalTestCase('load_toml_b', 'project', 'Example Project', str),
        RetrievalTestCase('load_toml_b', 'tool.ruff.line-length', 88, int),
        RetrievalTestCase(
            'load_toml_b', 'tool.ruff.lint.pydocstyle.convention', 'numpy', str
        ),
        RetrievalTestCase('load_toml_b', 'main_table.name', 'Main Table', str),
        RetrievalTestCase(
            'load_toml_b',
            'main_table.description',
            'This is the main table containing an array of nested tables.',
            str
        ),
        RetrievalTestCase(
            'load_toml_b',
            'main_table.sub_tables.name',
            ["Sub Table 1", "Sub Table 2"],
            str
        ),
        RetrievalTestCase('load_toml_b', 'main_table.sub_tables.value', [10, 20], int),
        RetrievalTestCase(
            'load_toml_b',
            'main_table.sub_tables',
            [
                {'name': 'Sub Table 1', 'value': 10},
                {'name': 'Sub Table 2', 'value': 20}
            ],
            items.Table
        ),
        RetrievalTestCase(
            'load_toml_b',
            'tool.ruff',
            {
                'line-length': 88,
                'lint': {'pydocstyle': {'convention': 'numpy'}}
            },
            items.Table
        ),
        RetrievalTestCase(
            'load_toml_b',
            'tool.ruff.lint.pydocstyle',
            {'convention': 'numpy'},
            items.InlineTable
        ),
        RetrievalTestCase('load_toml_c', 'project', 'Example Project', str),
        RetrievalTestCase(
            'load_toml_c', 'tool.ruff.lint.pydocstyle.convention', 'numpy', str
        ),
        RetrievalTestCase('load_toml_c', 'tool.ruff.line-length', 88, int),
        RetrievalTestCase('load_toml_c', 'tool.rye.managed', True, bool),
        RetrievalTestCase(
            'load_toml_c',
            'tool.rye.dev-dependencies',
            ['ruff>=0.4.4', 'mypy>=0.812', 'sphinx>=3.5', 'setuptools>=56.0'],
            str   
        ),
        RetrievalTestCase(
            'load_toml_c',
            'tool.ruff.lint.pydocstyle',
            {'convention': 'numpy'},
            items.InlineTable
        ),
        RetrievalTestCase(
            'load_toml_c',
            'tool.ruff',
            {
                'line-length': 88,
                'lint': {'pydocstyle': {'convention': 'numpy'}}
            },
            OutOfOrderTableProxy
        )
    ]
)
def test_retrieval_from_toml_document(
    test_case: RetrievalTestCase, request: pytest.FixtureRequest
) -> None:
    """Function to test the functionality of `get_attribute_from_toml_source`."""
    toml_document: TOMLDocument = request.getfixturevalue(test_case.fixture)
    toml_structure = get_attribute_from_toml_source(
        hierarchy=test_case.hierarchy, toml_source=toml_document
    )
    assert toml_structure == test_case.value
    assert is_toml_instance(
        test_case.value_type, hierarchy=test_case.hierarchy, toml_source=toml_document
    )