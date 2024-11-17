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

@dataclass(frozen=True)
class RetreivalTestCase:
    """"""
    hierarchy: str
    value: Any
    value_type: Type[Any]


def validate_retrieval(test_case: RetreivalTestCase, document: TOMLDocument) -> None:
    """"""
    toml_structure = get_attribute_from_toml_source(
        hierarchy=test_case.hierarchy, toml_source=document
    )
    assert toml_structure == test_case.value
    assert is_toml_instance(
        test_case.value_type, hierarchy=test_case.hierarchy, toml_source=document
    )


@pytest.mark.parametrize(
    'test_case',
    [
        RetreivalTestCase('project.name', 'Example Project', str),
        RetreivalTestCase(
            'details.description', 'A sample project configuration', str
        ),
        RetreivalTestCase('members.name', ['Alice', 'Bob'], str),
        RetreivalTestCase(
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
        RetreivalTestCase(
            'members.roles',
            [
                [{'role': 'Developer'}, {'role': 'Designer'}],
                [{'role': 'Manager'}]
            ],
            items.AoT
        ),
        RetreivalTestCase(
            'members.roles.role', ['Developer', 'Designer', 'Manager'], str
        )
    ]
)
def test_retrieval_from_toml_a(
    test_case: RetreivalTestCase, load_toml_a: TOMLDocument
) -> None:
    """"""
    validate_retrieval(test_case=test_case, document=load_toml_a)


@pytest.mark.parametrize(
    'test_case',
    [
        RetreivalTestCase('project', 'Example Project', str),
        RetreivalTestCase('tool.ruff.line-length', 88, int),
        RetreivalTestCase(
            'tool.ruff.lint.pydocstyle.convention', 'numpy', str
        ),
        RetreivalTestCase('main_table.name', 'Main Table', str),
        RetreivalTestCase(
            'main_table.description',
            'This is the main table containing an array of nested tables.',
            str
        ),
        RetreivalTestCase(
            'main_table.sub_tables.name', ["Sub Table 1", "Sub Table 2"], str
        ),
        RetreivalTestCase('main_table.sub_tables.value', [10, 20], int),
        RetreivalTestCase(
            'main_table.sub_tables',
            [
                {'name': 'Sub Table 1', 'value': 10},
                {'name': 'Sub Table 2', 'value': 20}
            ],
            items.Table
        ),
        RetreivalTestCase(
            'tool.ruff',
            {
                'line-length': 88,
                'lint': {'pydocstyle': {'convention': 'numpy'}}
            },
            items.Table
        ),
        RetreivalTestCase(
            'tool.ruff.lint.pydocstyle', {'convention': 'numpy'}, items.InlineTable
        )
    ]
)
def test_retrieval_from_toml_b(
    test_case: RetreivalTestCase, load_toml_b: TOMLDocument
) -> None:
    """"""
    validate_retrieval(test_case=test_case, document=load_toml_b)


@pytest.mark.parametrize(
    'test_case',
    [
        RetreivalTestCase('project', 'Example Project', str),
        RetreivalTestCase(
            'tool.ruff.lint.pydocstyle.convention', 'numpy', str
        ),
        RetreivalTestCase('tool.ruff.line-length', 88, int),
        RetreivalTestCase('tool.rye.managed', True, bool),
        RetreivalTestCase(
            'tool.rye.dev-dependencies',
            ['ruff>=0.4.4', 'mypy>=0.812', 'sphinx>=3.5', 'setuptools>=56.0'],
            str   
        ),
        RetreivalTestCase(
            'tool.ruff.lint.pydocstyle', {'convention': 'numpy'}, items.InlineTable
        ),
        RetreivalTestCase(
            'tool.ruff',
            {
                'line-length': 88,
                'lint': {'pydocstyle': {'convention': 'numpy'}}
            },
            OutOfOrderTableProxy
        )
    ]
)
def test_retrieval_from_toml_c(
    test_case: RetreivalTestCase, load_toml_c: TOMLDocument
) -> None:
    """"""
    validate_retrieval(test_case=test_case, document=load_toml_c)
