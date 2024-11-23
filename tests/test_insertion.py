from dataclasses import dataclass
from typing import (
    Any,
    Literal
)

import pytest
from tomlkit import TOMLDocument
from tomlkit_extras import (
    attribute_insert,
    container_insert,
    general_insert,
    get_attribute_from_toml_source,
    get_positions
)

from tests.typing import FixtureFunction

@dataclass(frozen=True)
class InsertionTestCase:
    """"""
    fixture: FixtureFunction
    insertion: Literal['general', 'attribute', 'container']
    hierarchy: str
    value: Any
    attribute: int
    container: int


@pytest.mark.parametrize(
    'test_case',
    [
        InsertionTestCase('load_toml_a', 'general', 'port', 443, 1, 2),
        InsertionTestCase(
            'load_toml_a',
            'general',
            'project.version',
            '0.1.0',
            2,
            2
        ),
        InsertionTestCase(
            'load_toml_a',
            'attribute',
            'title',
            'Example TOML Document',
            1,
            1
        ),
        InsertionTestCase(
            'load_toml_a',
            'attribute',
            'project.readme',
            'README.md',
            2,
            2
        ),
        InsertionTestCase(
            'load_toml_a',
            'container',
            'hosts',
            ["alpha", "omega", "beta"],
            2,
            2
        ),
        InsertionTestCase(
            'load_toml_b',
            'attribute',
            'title',
            'Example TOML Document',
            2, 
            2
        ),
        InsertionTestCase(
            'load_toml_b',
            'container',
            'hosts',
            ["alpha", "omega", "beta"],
            3,
            4
        ),
        InsertionTestCase(
            'load_toml_b',
            'container',
            'name',
            'Tom Preston-Werner',
            4,
            6
        ),
        InsertionTestCase(
            'load_toml_b',
            'container',
            'tool.ruff.lint.cache',
            True,
            1,
            2
        ),
        InsertionTestCase(
            'load_toml_c',
            'attribute',
            'tool.ruff.lint.pydocstyle.select',
            ["D200"],
            1,
            1
        ),
        InsertionTestCase(
            'load_toml_c',
            'container',
            'tool.ruff.lint.exclude',
            ["tests/", "docs/conf.py"],
            2,
            3
        )
    ]
)
def test_insertion_into_toml_document(
    test_case: InsertionTestCase, request: pytest.FixtureRequest
) -> None:
    """"""
    toml_document: TOMLDocument = request.getfixturevalue(test_case.fixture)

    # Generate the common insertion arguments
    insertion_args = {
        'hierarchy': test_case.hierarchy,
        'toml_source': toml_document,
        'insertion': test_case.value
    }

    # Based on insertion type, perform a specific insertion
    if test_case.insertion == 'general':
        general_insert(**insertion_args)
    elif test_case.insertion == 'attribute':
        attribute_insert(**insertion_args, position=test_case.attribute)
    else:
        container_insert(**insertion_args, position=test_case.container)

    # After insertion, retrieve value that was inserted and verify
    # that the value was indeed inserted
    inserted_attribute = get_attribute_from_toml_source(
        hierarchy=test_case.hierarchy, toml_source=toml_document
    )
    assert inserted_attribute == test_case.value
    
    # Retrieve and validate the positions of the value inserted
    attribute_pos, container_pos = get_positions(
        hierarchy=test_case.hierarchy, toml_source=toml_document
    )
    assert attribute_pos == attribute_pos
    assert container_pos == container_pos
