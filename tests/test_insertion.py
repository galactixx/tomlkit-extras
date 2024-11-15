from dataclasses import dataclass
import copy
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

@dataclass(frozen=True)
class InsertionTestCase:
    """"""
    insertion: Literal['general', 'attribute', 'container']
    hierarchy: str
    value: Any
    attribute: int
    container: int


def validate_insertion(
    test_case: InsertionTestCase, toml_document: TOMLDocument
) -> None:
    """"""
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


@pytest.fixture(scope='module')
def load_toml_a_insert(load_toml_a: TOMLDocument) -> TOMLDocument:
    """"""
    return copy.deepcopy(load_toml_a)


@pytest.fixture(scope='module')
def load_toml_b_insert(load_toml_b: TOMLDocument) -> TOMLDocument:
    """"""
    return copy.deepcopy(load_toml_b)


@pytest.fixture(scope='module')
def load_toml_c_insert(load_toml_c: TOMLDocument) -> TOMLDocument:
    """"""
    return copy.deepcopy(load_toml_c)


@pytest.mark.parametrize(
    'test_case',
    [
        InsertionTestCase('general', 'port', 443, 1, 2),
        InsertionTestCase('general', 'project.version', '0.1.0', 2, 2),
        InsertionTestCase(
            'attribute',
            'title',
            'Example TOML Document',
            1,
            1
        ),
        InsertionTestCase(
            'attribute',
            'project.readme',
            'README.md',
            2,
            2
        ),
        InsertionTestCase(
            'container',
            'hosts',
            ["alpha", "omega", "beta"],
            2,
            2
        )
    ]
)
def test_insertion_toml_a(
    test_case: InsertionTestCase, load_toml_a_insert: TOMLDocument
) -> None:
    """"""
    validate_insertion(test_case=test_case, toml_document=load_toml_a_insert)


@pytest.mark.parametrize(
    'test_case',
    [
        InsertionTestCase('attribute', 'title', 'Example TOML Document', 2, 2),
        InsertionTestCase(
            'container',
            'hosts',
            ["alpha", "omega", "beta"],
            3,
            4
        ),
        InsertionTestCase(
            'container',
            'name',
            'Tom Preston-Werner',
            4,
            6
        ),
        InsertionTestCase(
            'container',
            'tool.ruff.lint.cache',
            True,
            1,
            2
        )
    ]
)
def test_insertion_toml_b(
    test_case: InsertionTestCase, load_toml_b_insert: TOMLDocument
) -> None:
    """"""
    validate_insertion(test_case=test_case, toml_document=load_toml_b_insert)

@pytest.mark.parametrize(
    'test_case',
    [
        InsertionTestCase(
            'attribute',
            'tool.ruff.lint.pydocstyle.select',
            ["D200"],
            1,
            1
        ),
        InsertionTestCase(
            'container',
            'tool.ruff.lint.exclude',
            ["tests/", "docs/conf.py"],
            2,
            3
        )
    ]
)
def test_insertion_toml_c(
    test_case: InsertionTestCase, load_toml_c_insert: TOMLDocument
) -> None:
    """"""
    validate_insertion(test_case=test_case, toml_document=load_toml_c_insert)