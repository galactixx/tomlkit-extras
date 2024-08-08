from tomlkit import items, TOMLDocument
from tomlkit.container import OutOfOrderTableProxy
from tomlkit_extensions import (
    get_attribute_from_toml_source,
    is_toml_instance,
    load_toml_file
)

def test_retrieval_from_toml_a() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_a.toml')

    HIERARCHY_PROJECT_NAME = 'project.name'

    project_name = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_PROJECT_NAME, toml_source=toml_document
    )
    assert project_name == "Example Project"
    assert is_toml_instance(
        items.String, hierarchy=HIERARCHY_PROJECT_NAME, toml_source=toml_document
    )
    assert is_toml_instance(
        str, hierarchy=HIERARCHY_PROJECT_NAME, toml_source=toml_document
    )

    HIERARCHY_DESCRIPTION = 'details.description'

    details_description = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_DESCRIPTION, toml_source=toml_document
    )
    assert details_description == "A sample project configuration"
    assert is_toml_instance(
        items.String, hierarchy=HIERARCHY_DESCRIPTION, toml_source=toml_document
    )
    assert is_toml_instance(
        str, hierarchy=HIERARCHY_DESCRIPTION, toml_source=toml_document
    )

    HIERARCHY_MEMBERS = 'members'

    members_array = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_MEMBERS, toml_source=toml_document
    )
    assert len(members_array) == 2
    assert is_toml_instance(
        items.AoT, hierarchy=HIERARCHY_MEMBERS, toml_source=toml_document
    )

    assert is_toml_instance(
        items.Table, hierarchy=HIERARCHY_MEMBERS, toml_source=toml_document, array_priority=False
    )

    HIERARCHY_MEMBERS_NAMES = 'members.name'

    members_names = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_MEMBERS_NAMES, toml_source=toml_document
    )
    assert isinstance(members_names, list) and len(members_names) == 2
    assert members_names == ['Alice', 'Bob']
    assert is_toml_instance(
        str, hierarchy=HIERARCHY_MEMBERS_NAMES, toml_source=toml_document
    )

    HIERARCHY_MEMBERS_ROLES = 'members.roles'

    members_roles = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_MEMBERS_ROLES, toml_source=toml_document
    )
    assert isinstance(members_roles, list) and len(members_roles) == 2
    assert all(isinstance(aot, items.AoT) for aot in members_roles)
    assert is_toml_instance(
        items.AoT, hierarchy=HIERARCHY_MEMBERS_ROLES, toml_source=toml_document
    )

    HIERARCHY_MEMBERS_ROLES_ROLE = 'members.roles.role'

    members_roles_role = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_MEMBERS_ROLES_ROLE, toml_source=toml_document
    )
    assert isinstance(members_roles_role, list) and len(members_roles_role) == 3
    assert is_toml_instance(
        items.String, hierarchy=HIERARCHY_MEMBERS_ROLES_ROLE, toml_source=toml_document
    )
    assert is_toml_instance(
        str, hierarchy=HIERARCHY_MEMBERS_ROLES_ROLE, toml_source=toml_document
    )


def test_retrieval_from_toml_b() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_b.toml')

    HIERARCHY_PROJECT = 'project'

    project = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_PROJECT, toml_source=toml_document
    )
    assert project == "Example Project"
    assert is_toml_instance(
        items.String, hierarchy=HIERARCHY_PROJECT, toml_source=toml_document
    )
    assert is_toml_instance(
        str, hierarchy=HIERARCHY_PROJECT, toml_source=toml_document
    )

    HIERARCHY_TOOL_RUFF = 'tool.ruff'

    assert is_toml_instance(
        items.Table, hierarchy=HIERARCHY_TOOL_RUFF, toml_source=toml_document
    )

    HIERARCHY_TOOL_RUFF_LINE = 'tool.ruff.line-length'

    line_length = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_TOOL_RUFF_LINE, toml_source=toml_document
    )
    assert line_length == 88
    assert is_toml_instance(
        items.Integer, hierarchy=HIERARCHY_TOOL_RUFF_LINE, toml_source=toml_document
    )
    assert is_toml_instance(
        int, hierarchy=HIERARCHY_TOOL_RUFF_LINE, toml_source=toml_document
    )

    HIERARCHY_RUFF_PYDOCSTYLE = 'tool.ruff.lint.pydocstyle'

    assert is_toml_instance(
        items.InlineTable, hierarchy=HIERARCHY_RUFF_PYDOCSTYLE, toml_source=toml_document
    )

    HIERARCHY_PYDOCSTYLE_CONVENTION = 'tool.ruff.lint.pydocstyle.convention'

    convention = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_PYDOCSTYLE_CONVENTION, toml_source=toml_document
    )
    assert convention == 'numpy'
    assert is_toml_instance(
        items.String, hierarchy=HIERARCHY_PYDOCSTYLE_CONVENTION, toml_source=toml_document
    )
    assert is_toml_instance(
        str, hierarchy=HIERARCHY_PYDOCSTYLE_CONVENTION, toml_source=toml_document
    )

    HIERARCHY_MAIN_TABLE_NAME = 'main_table.name'

    main_table_name = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_MAIN_TABLE_NAME, toml_source=toml_document
    )
    assert main_table_name == 'Main Table'

    HIERARCHY_MAIN_TABLE_DESCRIPTION = 'main_table.description'
   
    main_table_description = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_MAIN_TABLE_DESCRIPTION, toml_source=toml_document
    )
    assert main_table_description == 'This is the main table containing an array of nested tables.'

    HIERARCHY_MAIN_SUB_TABLES = 'main_table.sub_tables'

    main_sub_tables = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_MAIN_SUB_TABLES, toml_source=toml_document, array_priority=False
    )
    assert isinstance(main_sub_tables, list) and len(main_sub_tables) == 2
    assert all(isinstance(table, items.Table) for table in main_sub_tables)

    assert is_toml_instance(
        items.AoT, hierarchy=HIERARCHY_MAIN_SUB_TABLES, toml_source=toml_document
    )
    assert is_toml_instance(
        items.Table, hierarchy=HIERARCHY_MAIN_SUB_TABLES, toml_source=toml_document, array_priority=False
    )  

    HIERARCHY_MAIN_SUB_NAME = 'main_table.sub_tables.name'

    main_sub_table_names = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_MAIN_SUB_NAME, toml_source=toml_document
    )
    assert main_sub_table_names == ["Sub Table 1", "Sub Table 2"]
    assert is_toml_instance(
        str, hierarchy=HIERARCHY_MAIN_SUB_NAME, toml_source=toml_document
    )

    HIERARCHY_MAIN_SUB_VALUE = 'main_table.sub_tables.value'

    main_sub_table_values = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_MAIN_SUB_VALUE, toml_source=toml_document
    )
    assert main_sub_table_values == [10, 20]
    assert is_toml_instance(
        int, hierarchy=HIERARCHY_MAIN_SUB_VALUE, toml_source=toml_document
    )


def test_retrieval_from_toml_c() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_c.toml')

    HIERARCHY_PROJECT = 'project'

    project = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_PROJECT, toml_source=toml_document
    )
    assert project == "Example Project"
    assert is_toml_instance(
        items.String, hierarchy=HIERARCHY_PROJECT, toml_source=toml_document
    )
    assert is_toml_instance(
        str, hierarchy=HIERARCHY_PROJECT, toml_source=toml_document
    )

    HIERARCHY_RUFF_PYDOCSTYLE = 'tool.ruff.lint.pydocstyle'

    assert is_toml_instance(
        items.InlineTable, hierarchy=HIERARCHY_RUFF_PYDOCSTYLE, toml_source=toml_document
    )

    HIERARCHY_PYDOCSTYLE_CONVENTION = 'tool.ruff.lint.pydocstyle.convention'

    convention = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_PYDOCSTYLE_CONVENTION, toml_source=toml_document
    )
    assert convention == 'numpy'
    assert is_toml_instance(
        items.String, hierarchy=HIERARCHY_PYDOCSTYLE_CONVENTION, toml_source=toml_document
    )
    assert is_toml_instance(
        str, hierarchy=HIERARCHY_PYDOCSTYLE_CONVENTION, toml_source=toml_document
    )

    HIERARCHY_TOOL_RUFF = 'tool.ruff'

    assert is_toml_instance(
        OutOfOrderTableProxy, hierarchy=HIERARCHY_TOOL_RUFF, toml_source=toml_document
    )

    HIERARCHY_TOOL_RUFF_LINE = 'tool.ruff.line-length'

    line_length = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_TOOL_RUFF_LINE, toml_source=toml_document
    )
    assert line_length == 88
    assert is_toml_instance(
        items.Integer, hierarchy=HIERARCHY_TOOL_RUFF_LINE, toml_source=toml_document
    )
    assert is_toml_instance(
        int, hierarchy=HIERARCHY_TOOL_RUFF_LINE, toml_source=toml_document
    )

    HIERARCHY_TOOL_RYE_MANAGED = 'tool.rye.managed'

    managed = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_TOOL_RYE_MANAGED, toml_source=toml_document
    )
    assert managed == True


    HIERARCHY_TOOL_RYE_DEV_DEPS = 'tool.rye.dev-dependencies'

    dev_dependencies = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_TOOL_RYE_DEV_DEPS, toml_source=toml_document
    )
    assert dev_dependencies == ['ruff>=0.4.4', 'mypy>=0.812', 'sphinx>=3.5', 'setuptools>=56.0']