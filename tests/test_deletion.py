from dataclasses import dataclass

from tomlkit import TOMLDocument
import pytest
from tomlkit_extras import (
    delete_from_toml_source,
    get_attribute_from_toml_source,
    InvalidHierarchyError
)

from tests.typing import FixtureModule

@dataclass(frozen=True)
class DeletionTestCase:
    """"""
    fixture: FixtureModule
    hierarchy: str


@pytest.mark.parametrize(
    'test_case',
    [
        DeletionTestCase('load_toml_a_module', 'project.name'),
        DeletionTestCase('load_toml_a_module', 'details.description'),
        DeletionTestCase('load_toml_a_module', 'members.roles.role'),
        DeletionTestCase('load_toml_a_module', 'members.name'),
        DeletionTestCase('load_toml_b_module', 'project'),
        DeletionTestCase('load_toml_b_module', 'tool.ruff.lint.pydocstyle.convention'),
        DeletionTestCase('load_toml_b_module', 'main_table.description'),
        DeletionTestCase(
            'load_toml_b_module', 'main_table.sub_tables.value'
        ),
        DeletionTestCase('load_toml_b_module', 'main_table.sub_tables.name'),
        DeletionTestCase('load_toml_b_module', 'tool.ruff'),
        DeletionTestCase('load_toml_b_module', 'main_table.name'),
        DeletionTestCase('load_toml_c_module', 'tool.ruff'),
        DeletionTestCase('load_toml_c_module', 'tool.rye'),
        DeletionTestCase('load_toml_c_module', 'project')
    ]
)
def test_deletion_from_toml_document(
    test_case: DeletionTestCase, request: pytest.FixtureRequest
) -> None:
    """"""
    toml_document: TOMLDocument = request.getfixturevalue(test_case.fixture)
    delete_from_toml_source(hierarchy=test_case.hierarchy, toml_source=toml_document)

    with pytest.raises(InvalidHierarchyError) as exc_info:
        _ = get_attribute_from_toml_source(
            hierarchy=test_case.hierarchy, toml_source=toml_document
        )

    assert str(exc_info.value) == (
        "Hierarchy specified does not exist in TOMLDocument instance"
    )


@pytest.mark.parametrize(
    'test_case',
    [
        DeletionTestCase('load_toml_c_module', 'tool.poetry'),
        DeletionTestCase('load_toml_c_module', 'tool.ruff')
    ]
)
def test_invalid_deletion(
    test_case: DeletionTestCase, request: pytest.FixtureRequest
) -> None:
    """"""
    toml_document: TOMLDocument = request.getfixturevalue(test_case.fixture)
    with pytest.raises(InvalidHierarchyError) as exc_info:
        delete_from_toml_source(hierarchy=test_case.hierarchy, toml_source=toml_document)
    assert str(exc_info.value) == "Hierarchy does not exist in TOML source space"
