from dataclasses import dataclass

import pytest
from tomlkit import TOMLDocument

from tests.typing import FixtureFunction
from tomlkit_extras import (
    InvalidHierarchyDeletionError,
    InvalidHierarchyRetrievalError,
    delete_from_toml_source,
    get_attribute_from_toml_source,
)


@dataclass(frozen=True)
class DeletionTestCase:
    """
    Dataclass representing a test case for the `delete_from_toml_source`
    function
    """

    fixture: FixtureFunction
    hierarchy: str


@pytest.mark.parametrize(
    "test_case",
    [
        DeletionTestCase("load_toml_a", "project.name"),
        DeletionTestCase("load_toml_a", "details.description"),
        DeletionTestCase("load_toml_a", "members.roles.role"),
        DeletionTestCase("load_toml_a", "members.name"),
        DeletionTestCase("load_toml_b", "project"),
        DeletionTestCase("load_toml_b", "tool.ruff.lint.pydocstyle.convention"),
        DeletionTestCase("load_toml_b", "main_table.description"),
        DeletionTestCase("load_toml_b", "main_table.sub_tables.value"),
        DeletionTestCase("load_toml_b", "main_table.sub_tables.name"),
        DeletionTestCase("load_toml_b", "tool.ruff"),
        DeletionTestCase("load_toml_b", "main_table.name"),
        DeletionTestCase("load_toml_c", "tool.ruff"),
        DeletionTestCase("load_toml_c", "tool.rye"),
        DeletionTestCase("load_toml_c", "project"),
    ],
)
def test_deletion_from_toml_document(
    test_case: DeletionTestCase, request: pytest.FixtureRequest
) -> None:
    """Function to test the functionality of `delete_from_toml_source`."""
    toml_document: TOMLDocument = request.getfixturevalue(test_case.fixture)
    delete_from_toml_source(hierarchy=test_case.hierarchy, toml_source=toml_document)

    with pytest.raises(InvalidHierarchyRetrievalError) as exc_info:
        _ = get_attribute_from_toml_source(
            hierarchy=test_case.hierarchy, toml_source=toml_document
        )

    assert exc_info.value.message == (
        "Hierarchy specified does not exist in TOMLDocument instance"
    )


@pytest.mark.parametrize(
    "test_case",
    [
        DeletionTestCase("load_toml_c", "tool.poetry.name"),
        DeletionTestCase("load_toml_c", "tool.ruff.lint.select"),
    ],
)
def test_invalid_deletion(
    test_case: DeletionTestCase, request: pytest.FixtureRequest
) -> None:
    """Function to test the error handling of `delete_from_toml_source`."""
    toml_document: TOMLDocument = request.getfixturevalue(test_case.fixture)
    with pytest.raises(InvalidHierarchyDeletionError) as exc_info:
        delete_from_toml_source(
            hierarchy=test_case.hierarchy, toml_source=toml_document
        )
    assert exc_info.value.message == "Hierarchy does not exist in TOML source space"
