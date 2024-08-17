from tomlkit.container import OutOfOrderTableProxy
from tomlkit import items, TOMLDocument
import pytest
from tomlkit_extras import (
    delete_from_toml_source,
    get_attribute_from_toml_source,
    load_toml_file,
    InvalidHierarchyError
)

def _retrieval_of_invalid_hierarchy(hierarchy: str, toml_document: TOMLDocument) -> None:
    """"""
    with pytest.raises(InvalidHierarchyError) as exc_info:
        _ = get_attribute_from_toml_source(
            hierarchy=hierarchy, toml_source=toml_document, array=False
        )

    assert str(exc_info.value) == (
        "Hierarchy specified does not exist in TOMLDocument instance"
    )


def _deletion_and_retrieval_test(hierarchy: str, toml_document: TOMLDocument) -> None:
    """"""
    delete_from_toml_source(hierarchy=hierarchy, toml_source=toml_document)
    _retrieval_of_invalid_hierarchy(hierarchy=hierarchy, toml_document=toml_document)


def test_deletion_from_toml_a() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_a.toml')

    HIERARCHY_PROJECT_NAME = 'project.name'

    project_name = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_PROJECT_NAME, toml_source=toml_document
    )
    assert isinstance(project_name, items.String)
    assert project_name.unwrap() == "Example Project"

    # Delete the "name" field from the "project" table. Since "name" is the
    # only field in this table, the following function call should result in
    # the deletion of the entire table
    _deletion_and_retrieval_test(hierarchy=HIERARCHY_PROJECT_NAME, toml_document=toml_document)

    # Delete all "role" fields from each table in the "members.roles" array
    # of tables. This should mirror the prior result
    HIERARCHY_MEMBERS_ROLES_ROLE = 'members.roles.role'

    members_roles_role_aot = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_MEMBERS_ROLES_ROLE, toml_source=toml_document, array=False
    )
    assert isinstance(members_roles_role_aot, list)
    assert len(members_roles_role_aot) == 3
    _deletion_and_retrieval_test(hierarchy=HIERARCHY_MEMBERS_ROLES_ROLE, toml_document=toml_document)

    HIERARCHY_DETAILS_DESCRIPTION = 'details.description'

    details_description = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_DETAILS_DESCRIPTION, toml_source=toml_document
    )
    assert isinstance(details_description, items.String)
    assert details_description.unwrap() == "A sample project configuration"
    _deletion_and_retrieval_test(hierarchy=HIERARCHY_DETAILS_DESCRIPTION, toml_document=toml_document)

    HIERARCHY_MEMBERS_NAME = 'members.name'

    members_name_aot = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_MEMBERS_NAME, toml_source=toml_document, array=False
    )
    assert isinstance(members_name_aot, list)
    assert len(members_name_aot) == 2
    _deletion_and_retrieval_test(hierarchy=HIERARCHY_MEMBERS_NAME, toml_document=toml_document)

    assert not toml_document


def test_deletion_from_toml_b() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_b.toml')

    HIERARCHY_PROJECT = 'project'

    project = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_PROJECT, toml_source=toml_document
    )
    assert isinstance(project, items.String)
    assert project.unwrap() == "Example Project"
    _deletion_and_retrieval_test(hierarchy=HIERARCHY_PROJECT, toml_document=toml_document)

    HIERARCHY_PYDOCSTYLE_CONVENTION = 'tool.ruff.lint.pydocstyle.convention'

    pydocstyle_convention = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_PYDOCSTYLE_CONVENTION, toml_source=toml_document
    )
    assert isinstance(pydocstyle_convention, items.String)
    assert pydocstyle_convention.unwrap() == "numpy"
    _deletion_and_retrieval_test(hierarchy=HIERARCHY_PYDOCSTYLE_CONVENTION, toml_document=toml_document)

    HIERARCHY_MAIN_DESCRIPTION = 'main_table.description'

    main_table_description = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_MAIN_DESCRIPTION, toml_source=toml_document
    )
    assert isinstance(main_table_description, items.String)
    assert main_table_description.unwrap() == "This is the main table containing an array of nested tables."
    _deletion_and_retrieval_test(hierarchy=HIERARCHY_MAIN_DESCRIPTION, toml_document=toml_document)

    HIERARCHY_MAIN_SUB_VALUE = 'main_table.sub_tables.value'

    sub_table_values = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_MAIN_SUB_VALUE, toml_source=toml_document
    )
    assert isinstance(sub_table_values, list)
    assert len(sub_table_values) == 2
    _deletion_and_retrieval_test(hierarchy=HIERARCHY_MAIN_SUB_VALUE, toml_document=toml_document)

    HIERARCHY_MAIN_SUB_TABLES = 'main_table.sub_tables'
    HIERARCHY_MAIN_SUB_NAME = 'main_table.sub_tables.name'

    sub_tables = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_MAIN_SUB_TABLES, toml_source=toml_document
    )
    assert isinstance(sub_tables, list)
    assert len(sub_tables) == 2
    _deletion_and_retrieval_test(hierarchy=HIERARCHY_MAIN_SUB_NAME, toml_document=toml_document)

    HIERARCHY_TOOL_RUFF_LINE = 'tool.ruff.line-length'

    tool_ruff_line_length = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_TOOL_RUFF_LINE, toml_source=toml_document
    )
    assert isinstance(tool_ruff_line_length, items.Integer)
    assert tool_ruff_line_length.unwrap() == 88
    delete_from_toml_source(hierarchy='tool.ruff', toml_source=toml_document)
    _retrieval_of_invalid_hierarchy(hierarchy='tool', toml_document=toml_document)

    HIERARCHY_MAIN_NAME = 'main_table.name'

    main_table_name = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_MAIN_NAME, toml_source=toml_document
    )
    assert isinstance(main_table_name, items.String)
    assert main_table_name.unwrap() == 'Main Table'
    delete_from_toml_source(hierarchy=HIERARCHY_MAIN_NAME, toml_source=toml_document)
    
    assert not toml_document


def test_deletion_from_toml_c() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_c.toml')

    HIERARCHY_TOOL_RUFF = 'tool.ruff'

    assert isinstance(
        get_attribute_from_toml_source(hierarchy=HIERARCHY_TOOL_RUFF, toml_source=toml_document),
        OutOfOrderTableProxy
    )
    _deletion_and_retrieval_test(hierarchy=HIERARCHY_TOOL_RUFF, toml_document=toml_document)

    HIERARCHY_TOOL_RYE = 'tool.rye'

    assert isinstance(
        get_attribute_from_toml_source(hierarchy=HIERARCHY_TOOL_RYE, toml_source=toml_document),
        items.Table
    )
    _deletion_and_retrieval_test(hierarchy=HIERARCHY_TOOL_RYE, toml_document=toml_document)

    HIERARCHY_PROJECT = 'project'

    assert len(toml_document) == 1
    assert toml_document[HIERARCHY_PROJECT] == "Example Project"
    delete_from_toml_source(hierarchy=HIERARCHY_PROJECT, toml_source=toml_document)

    assert not toml_document


def test_deletion_errors() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_c.toml')

    HIERARCHY_TOOL_POETRY = 'tool.poetry'

    with pytest.raises(InvalidHierarchyError) as exc_info:
        delete_from_toml_source(hierarchy=HIERARCHY_TOOL_POETRY, toml_source=toml_document)
    assert str(exc_info.value) == "Hierarchy does not exist in TOML source space"

    HIERARCHY_TOOL_RUFF = 'tool.ruff'

    delete_from_toml_source(hierarchy=HIERARCHY_TOOL_RUFF, toml_source=toml_document)

    with pytest.raises(InvalidHierarchyError) as exc_info:
        delete_from_toml_source(hierarchy=HIERARCHY_TOOL_RUFF, toml_source=toml_document)
    
    assert str(exc_info.value) == "Hierarchy does not exist in TOML source space"