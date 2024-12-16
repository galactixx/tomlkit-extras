from dataclasses import dataclass
from typing import (
    Any,
    List,
    Literal,
    Optional,
    Type
)

import pytest
from tomlkit import TOMLDocument, items
from tomlkit_extras import (
    attribute_insert,
    container_insert,
    general_insert,
    get_attribute_from_toml_source,
    get_positions,
    Hierarchy,
    TOMLInsertionError
)

from tests.typing import FixtureFunction

@dataclass(frozen=True)
class BaseInsertionTestCase(object):
    """
    Base dataclass representing a test case for any of the insertion
    functions.
    """
    fixture: FixtureFunction
    insertion: Literal['general', 'attribute', 'container']
    hierarchy: Optional[str]
    key: Optional[str]
    value: Any


@dataclass(frozen=True)
class InsertionTestCase(BaseInsertionTestCase):
    """
    Dataclass representing a test case for the `general_insert`,
    `attribute_insert`, and `container_insert` functions.
    """
    attribute: int
    container: int


@dataclass(frozen=True)
class InvalidInsertionTestCase(BaseInsertionTestCase):
    """Dataclass representing an invalid insertion test case."""
    message: str
    struct_type: Type[Any]


def consolidate_hierarchy(hierarchy: Optional[str], key: Optional[str]) -> Hierarchy:
    """Consolidates a hierarchy from two optional string arguments."""
    full_hierarchy: List[str] = []
    if hierarchy is not None:
        full_hierarchy.extend(hierarchy.split('.'))

    if key is not None:
        full_hierarchy.append(key)

    return Hierarchy.from_list_hierarchy(hierarchy=full_hierarchy)
        

@pytest.mark.parametrize(
    'test_case',
    [
        InsertionTestCase(
            'load_toml_a',
            'general',
            None,
            'port',
            443,
            1,
            2
        ),
        InsertionTestCase(
            'load_toml_a',
            'general',
            'project',
            'version',
            '0.1.0',
            2,
            2
        ),
        InsertionTestCase(
            'load_toml_a',
            'attribute',
            None,
            'title',
            'Example TOML Document',
            1,
            1
        ),
        InsertionTestCase(
            'load_toml_a',
            'attribute',
            'project',
            'readme',
            'README.md',
            2,
            2
        ),
        InsertionTestCase(
            'load_toml_a',
            'container',
            None,
            'hosts',
            ["alpha", "omega", "beta"],
            2,
            2
        ),
        InsertionTestCase(
            'load_toml_b',
            'attribute',
            None,
            'title',
            'Example TOML Document',
            2, 
            2
        ),
        InsertionTestCase(
            'load_toml_b',
            'container',
            None,
            'hosts',
            ["alpha", "omega", "beta"],
            3,
            4
        ),
        InsertionTestCase(
            'load_toml_b',
            'container',
            None,
            'name',
            'Tom Preston-Werner',
            4,
            6
        ),
        InsertionTestCase(
            'load_toml_b',
            'container',
            'tool.ruff.lint',
            'cache',
            True,
            1,
            2
        ),
        InsertionTestCase(
            'load_toml_c',
            'attribute',
            'tool.ruff.lint.pydocstyle',
            'select',
            ["D200"],
            1,
            1
        ),
        InsertionTestCase(
            'load_toml_c',
            'container',
            'tool.ruff.lint',
            'exclude',
            ["tests/", "docs/conf.py"],
            2,
            3
        )
    ]
)
def test_insertion_into_toml_document(
    test_case: InsertionTestCase, request: pytest.FixtureRequest
) -> None:
    """
    Function to test the functionality of the `general_insert`,
    `attribute_insert`, and `container_insert` functions.
    """
    toml_document: TOMLDocument = request.getfixturevalue(test_case.fixture)

    # Generate the common insertion arguments
    insertion_args = {
        'hierarchy': test_case.hierarchy,
        'key': test_case.key,
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
    hierarchy: Hierarchy = consolidate_hierarchy(
        hierarchy=test_case.hierarchy, key=test_case.key
    )

    inserted_object = get_attribute_from_toml_source(
        hierarchy=hierarchy, toml_source=toml_document
    )
    assert inserted_object == test_case.value
    
    # Retrieve and validate the positions of the value inserted
    attribute_pos, container_pos = get_positions(
        hierarchy=hierarchy, toml_source=toml_document
    )
    assert attribute_pos == attribute_pos
    assert container_pos == container_pos


@pytest.mark.parametrize(
    'test_case',
    [
        InvalidInsertionTestCase(
            'load_toml_a',
            'general',
            'members.roles',
            'name',
            'Joe Biden',
            'Hierarchy maps to multiple items, insertion is not supported',
            list
        ),
        InvalidInsertionTestCase(
            'load_toml_b',
            'general',
            'tool.ruff.line-length',
            'name',
            'Joe Biden',
            'Hierarchy maps to a structure that does not support insertion',
            items.Integer
        )
    ]
)
def test_invalid_insertion(
    test_case: InvalidInsertionTestCase, request: pytest.FixtureRequest
) -> None:
    """
    Function that tests the error handling of the insertion functions.
    """
    toml_document: TOMLDocument = request.getfixturevalue(test_case.fixture)

    with pytest.raises(TOMLInsertionError) as exc_info:
        general_insert(
            hierarchy=test_case.hierarchy,
            toml_source=toml_document,
            insertion=test_case.value
        )
    assert exc_info.value.message == test_case.message
    assert exc_info.value.struct_type == test_case.struct_type