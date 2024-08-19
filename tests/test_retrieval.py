from typing import (
    Any,
    Type
)

from tomlkit import items, TOMLDocument
from tomlkit.container import OutOfOrderTableProxy
from tomlkit_extras import (
    get_attribute_from_toml_source,
    is_toml_instance,
    load_toml_file
)

def _attribute_value_test(hierarchy: str, attr_value: Any, toml_document: TOMLDocument) -> None:
    """"""
    assert get_attribute_from_toml_source(
        hierarchy=hierarchy, toml_source=toml_document
    ) == attr_value


def _double_toml_type_test(
    item_type: Type[items.Item], primitive_type: Type[Any], *, hierarchy: str, toml_document: TOMLDocument    
) -> None:
    """"""
    assert is_toml_instance(item_type, hierarchy=hierarchy, toml_source=toml_document)
    assert is_toml_instance(primitive_type, hierarchy=hierarchy, toml_source=toml_document)


def test_retrieval_from_toml_a() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_a.toml')

    # Testing for project.name hierarchy
    _attribute_value_test(
        hierarchy='project.name', attr_value='Example Project', toml_document=toml_document
    )
    _double_toml_type_test(items.String, str, hierarchy='project.name', toml_document=toml_document)

    # Testing for details.description hierarchy
    _attribute_value_test(
        hierarchy='details.description',
        attr_value='A sample project configuration',
        toml_document=toml_document
    )
    _double_toml_type_test(
        items.String, str, hierarchy='details.description', toml_document=toml_document  
    )

    # Testing for members.name hierarchy
    _attribute_value_test(
        hierarchy='members.name', attr_value=['Alice', 'Bob'], toml_document=toml_document
    )
    assert is_toml_instance(str, hierarchy='members.name', toml_source=toml_document)

    # Testing for the members hierarchy
    members = get_attribute_from_toml_source(hierarchy='members', toml_source=toml_document)
    assert isinstance(members, items.AoT) and len(members) == 2
    assert is_toml_instance(items.AoT, hierarchy='members', toml_source=toml_document)
    assert is_toml_instance(
        items.Table, hierarchy='members', toml_source=toml_document, array=False
    )

    # Testing for the members.roles hierarchy
    members_roles = get_attribute_from_toml_source(hierarchy='members.roles', toml_source=toml_document)
    assert isinstance(members_roles, list) and len(members_roles) == 2
    assert is_toml_instance(items.AoT, hierarchy='members.roles', toml_source=toml_document)

    # Testing for the members.roles.role hierarchy
    members_roles_role = get_attribute_from_toml_source(hierarchy='members.roles.role', toml_source=toml_document) 
    assert isinstance(members_roles_role, list) and len(members_roles_role) == 3
    _double_toml_type_test(
        items.String, str, hierarchy='members.roles.role', toml_document=toml_document  
    )


def test_retrieval_from_toml_b() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_b.toml')

    # Testing for project hierarchy
    _attribute_value_test(
        hierarchy='project', attr_value='Example Project', toml_document=toml_document
    )
    _double_toml_type_test(items.String, str, hierarchy='project', toml_document=toml_document)

    # Testing for tool.ruff hierarchy
    assert is_toml_instance(
        items.Table, hierarchy='tool.ruff', toml_source=toml_document
    )

    # Testing for tool.ruff.line-length hierarchy
    _attribute_value_test(hierarchy='tool.ruff.line-length', attr_value=88, toml_document=toml_document)
    _double_toml_type_test(
        items.Integer, int, hierarchy='tool.ruff.line-length', toml_document=toml_document
    )

    # Testing for tool.ruff.lint.pydocstyle hierarchy
    assert is_toml_instance(
        items.InlineTable, hierarchy='tool.ruff.lint.pydocstyle', toml_source=toml_document
    )

    # Testing for tool.ruff.lint.pydocstyle.convention hierarchy
    _attribute_value_test(
        hierarchy='tool.ruff.lint.pydocstyle.convention',
        attr_value='numpy',
        toml_document=toml_document
    )
    _double_toml_type_test(
        items.String,
        str,
        hierarchy='tool.ruff.lint.pydocstyle.convention',
        toml_document=toml_document
    )

    # Testing for main_table.name hierarchy
    _attribute_value_test(
        hierarchy='main_table.name', attr_value='Main Table', toml_document=toml_document
    )

    # Testing for main_table.description hierarchy
    _attribute_value_test(
        hierarchy='main_table.description',
        attr_value='This is the main table containing an array of nested tables.',
        toml_document=toml_document
    )

    # Testing for main_table.sub_tables hierarchy
    main_table_sub_tables = get_attribute_from_toml_source(
        hierarchy='main_table.sub_tables', toml_source=toml_document
    )

    assert isinstance(main_table_sub_tables, items.AoT) and len(main_table_sub_tables) == 2
    assert is_toml_instance(items.AoT, hierarchy='main_table.sub_tables', toml_source=toml_document)
    assert is_toml_instance(
        items.Table, hierarchy='main_table.sub_tables', toml_source=toml_document, array=False
    )  

    # Testing for main_table.sub_tables.name hierarchy
    _attribute_value_test(
        hierarchy='main_table.sub_tables.name',
        attr_value=["Sub Table 1", "Sub Table 2"],
        toml_document=toml_document
    )
    assert is_toml_instance(str, hierarchy='main_table.sub_tables.name', toml_source=toml_document)

    # Testing for main_table.sub_tables.value hierarchy
    _attribute_value_test(
        hierarchy='main_table.sub_tables.value', attr_value=[10, 20], toml_document=toml_document
    )
    assert is_toml_instance(
        int, hierarchy='main_table.sub_tables.value', toml_source=toml_document
    )


def test_retrieval_from_toml_c() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_c.toml')
    
    # Testing for project hierarchy
    _attribute_value_test(
        hierarchy='project', attr_value='Example Project', toml_document=toml_document
    )
    _double_toml_type_test(items.String, str, hierarchy='project', toml_document=toml_document)

    # Testing for tool.ruff.lint.pydocstyle hierarchy
    assert is_toml_instance(
        items.InlineTable, hierarchy='tool.ruff.lint.pydocstyle', toml_source=toml_document
    )

    # Testing for tool.ruff.lint.pydocstyle.convention hierarchy
    _attribute_value_test(
        hierarchy='tool.ruff.lint.pydocstyle.convention',
        attr_value='numpy',
        toml_document=toml_document
    )
    _double_toml_type_test(
        items.String,
        str,
        hierarchy='tool.ruff.lint.pydocstyle.convention',
        toml_document=toml_document
    )

    # Testing for tool.ruff hierarchy
    assert is_toml_instance(
        OutOfOrderTableProxy, hierarchy='tool.ruff', toml_source=toml_document
    )

    # Testing for tool.ruff.line-length hierarchy
    _attribute_value_test(hierarchy='tool.ruff.line-length', attr_value=88, toml_document=toml_document)
    _double_toml_type_test(
        items.Integer, int, hierarchy='tool.ruff.line-length', toml_document=toml_document
    )

    # Testing for tool.rye.managed hierarchy
    _attribute_value_test(
        hierarchy='tool.rye.managed', attr_value=True, toml_document=toml_document
    )

    # Testing for tool.rye.dev-dependencies hierarchy
    _attribute_value_test(
        hierarchy='tool.rye.dev-dependencies',
        attr_value=['ruff>=0.4.4', 'mypy>=0.812', 'sphinx>=3.5', 'setuptools>=56.0'],
        toml_document=toml_document
    )