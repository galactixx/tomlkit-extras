from tomlkit import items, TOMLDocument
from tomlkit_extras import (
    get_attribute_from_toml_source,
    get_array_field_comment,
    get_comments,
    Hierarchy,
    load_toml_file
)

def test_comments_toml_a() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_a.toml')

    # Retrieve all comments from the top-level document space
    document_comments = get_comments(toml_source=toml_document)
    assert document_comments == [(1, '# this is a document comment')]

    # Test a few tables that do not have any comments
    HIERARCHY_PROJECT = 'project'
    project_comments = get_comments(toml_source=toml_document, hierarchy=HIERARCHY_PROJECT)
    assert project_comments is None

    HIERARCHY_DETAILS = 'details'
    details_comments = get_comments(toml_source=toml_document, hierarchy=HIERARCHY_DETAILS)
    assert details_comments is None

    HIERARCHY_MEMBERS = 'members'
    members_comments = get_comments(toml_source=toml_document, hierarchy=HIERARCHY_MEMBERS)
    assert members_comments is None


def test_comments_toml_b() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_b.toml')

    # Retrieve all comments from the top-level document space
    document_comments = get_comments(toml_source=toml_document)
    assert document_comments == [(4, '# this is a document comment')]

    # Retrieve all table comments from the tool.ruff.lint table
    HIERARCHY_RUFF_LINT = Hierarchy.from_str_hierarchy(hierarchy='tool.ruff.lint')
    RUFF_LINT_COMMENTS = [
        (1, '# this is the first comment for lint table'),
        (2, '# this is the second comment for lint table')
    ]

    ruff_lint_comments = get_comments(toml_source=toml_document, hierarchy=HIERARCHY_RUFF_LINT)
    assert ruff_lint_comments == RUFF_LINT_COMMENTS

    # Retrieve from the lint table after navigating to the relevant location
    tool_ruff_lint: items.Array = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_RUFF_LINT, toml_source=toml_document
    )
    ruff_lint_comments_again = get_comments(toml_source=tool_ruff_lint)
    assert ruff_lint_comments_again == RUFF_LINT_COMMENTS

    # Test a few tables that do not have any comments
    HIERARCHY_MAIN_TABLE = 'main_table'
    main_table_comments = get_comments(toml_source=toml_document, hierarchy=HIERARCHY_MAIN_TABLE)
    assert main_table_comments is None


def test_comments_toml_c() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_c.toml')

    # Retrieve all comments from the top-level document space
    document_comments = get_comments(toml_source=toml_document)
    assert document_comments == [(1, '# this is a document comment')]

    # Retrieve all table comments from the tool.ruff.lint table
    HIERARCHY_RUFF_LINT = Hierarchy.from_str_hierarchy(hierarchy='tool.ruff.lint')
    RUFF_LINT_COMMENTS = [(3, '# this is the first comment for lint table')]

    ruff_lint_comments = get_comments(toml_source=toml_document, hierarchy=HIERARCHY_RUFF_LINT)
    assert ruff_lint_comments == RUFF_LINT_COMMENTS

    # Retrieve from the lint table after navigating to the relevant location
    tool_ruff_lint: items.Array = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_RUFF_LINT, toml_source=toml_document
    )
    ruff_lint_comments_again = get_comments(toml_source=tool_ruff_lint)
    assert ruff_lint_comments_again == RUFF_LINT_COMMENTS

    # Retrieve all table comments from the tool.ruff table
    HIERARCHY_RUFF = Hierarchy.from_str_hierarchy(hierarchy='tool.ruff')

    ruff_comments = get_comments(toml_source=toml_document, hierarchy=HIERARCHY_RUFF)
    assert ruff_comments == [(2, '# this is a tool.ruff comment')]

    # Test a table that does not have any comments
    HIERARCHY_RYE = Hierarchy.from_str_hierarchy(hierarchy='tool.rye')

    rye_comments = get_comments(toml_source=toml_document, hierarchy=HIERARCHY_RYE)
    assert rye_comments is None

    # Grab all array comments
    dev_dependencies_array: items.Array = get_attribute_from_toml_source(
        hierarchy='tool.rye.dev-dependencies', toml_source=toml_document
    )

    ruff_comment = get_array_field_comment(array=dev_dependencies_array, array_item='ruff>=0.4.4')
    assert ruff_comment == '# ruff version'

    ruff_comment = get_array_field_comment(array=dev_dependencies_array, array_item='mypy>=0.812')
    assert ruff_comment is None

    ruff_comment = get_array_field_comment(array=dev_dependencies_array, array_item='sphinx>=3.5')
    assert ruff_comment == '# sphinx version'

    ruff_comment = get_array_field_comment(array=dev_dependencies_array, array_item='setuptools>=56.0')
    assert ruff_comment == '# setuptools version'