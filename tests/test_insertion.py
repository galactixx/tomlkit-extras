from tomlkit import items, TOMLDocument
from tomlkit_extras import (
    attribute_insertion_into_toml_source,
    container_insertion_into_toml_source,
    general_insertion_into_toml_source,
    get_attribute_from_toml_source,
    get_positions,
    load_toml_file
)

def _inserted_position_test(
    attribute_pos: int, container_pos: int, hierarchy: str, toml_document: TOMLDocument
) -> None:
    """"""
    attribute_pos, container_pos = get_positions(hierarchy=hierarchy, toml_source=toml_document)
    assert attribute_pos == attribute_pos
    assert container_pos == container_pos


def test_insertion_into_toml_a() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_a.toml')

    # Insert a single field in the top-level document space
    HIERARCHY_PORT = 'port'
    general_insertion_into_toml_source(
        hierarchy=HIERARCHY_PORT, toml_source=toml_document, insertion=443
    )
    assert toml_document[HIERARCHY_PORT] == 443

    # The expectation is that the field should be in an attribute position of 1, since there are no
    # other fields in the top-level document space. And should be in a container position of 2
    _inserted_position_test(
        attribute_pos=1, container_pos=2, hierarchy=HIERARCHY_PORT, toml_document=toml_document
    )

    HIERARCHY_TITLE = 'title'
    attribute_insertion_into_toml_source(
        hierarchy=HIERARCHY_TITLE, toml_source=toml_document, insertion="Example TOML Document", position=1
    )
    assert toml_document[HIERARCHY_TITLE] == "Example TOML Document"
    _inserted_position_test(
        attribute_pos=1, container_pos=1, hierarchy=HIERARCHY_TITLE, toml_document=toml_document
    )

    # Insert right after the comment "# this is a document comment"
    HIERARCHY_HOSTS = 'hosts'
    container_insertion_into_toml_source(
        hierarchy=HIERARCHY_HOSTS, toml_source=toml_document, insertion=["alpha", "omega", "beta"], position=2
    )
    assert toml_document[HIERARCHY_HOSTS] == ["alpha", "omega", "beta"]
    _inserted_position_test(
        attribute_pos=2, container_pos=2, hierarchy=HIERARCHY_HOSTS, toml_document=toml_document
    )

    # Perform a general insertion into the project table, should be inserted
    # right after the "name" field
    HIERARCHY_PROJECT_VERSION = 'project.version'
    general_insertion_into_toml_source(
        hierarchy=HIERARCHY_PROJECT_VERSION, toml_source=toml_document, insertion="0.1.0"
    )
    project_version = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_PROJECT_VERSION, toml_source=toml_document
    )
    assert isinstance(project_version, items.String)
    assert project_version.unwrap() == '0.1.0'
    _inserted_position_test(
        attribute_pos=2, container_pos=2, hierarchy=HIERARCHY_PROJECT_VERSION, toml_document=toml_document
    )

    HIERARCHY_PROJECT_README = 'project.readme'

    # Perform an insertion of field in between the "name" and "version" fields
    attribute_insertion_into_toml_source(
        hierarchy=HIERARCHY_PROJECT_README, toml_source=toml_document, insertion="README.md", position=2
    )
    project_readme = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_PROJECT_README, toml_source=toml_document
    )
    assert isinstance(project_readme, items.String)
    assert project_readme.unwrap() == 'README.md'
    _inserted_position_test(
        attribute_pos=2, container_pos=2, hierarchy=HIERARCHY_PROJECT_README, toml_document=toml_document
    )


def test_insertion_into_toml_b() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_b.toml')

    HIERARCHY_TITLE = 'title'
    attribute_insertion_into_toml_source(
        hierarchy=HIERARCHY_TITLE, toml_source=toml_document, insertion="Example TOML Document", position=2
    )
    assert toml_document[HIERARCHY_TITLE] == "Example TOML Document"
    _inserted_position_test(
        attribute_pos=2, container_pos=2, hierarchy=HIERARCHY_TITLE, toml_document=toml_document
    )

    # Insert the "hosts" field right after the first whitespace but before the first comment
    HIERARCHY_HOSTS = 'hosts'
    container_insertion_into_toml_source(
        hierarchy=HIERARCHY_HOSTS, toml_source=toml_document, insertion=["alpha", "omega", "beta"], position=4
    )
    assert toml_document[HIERARCHY_HOSTS] == ["alpha", "omega", "beta"]
    _inserted_position_test(
        attribute_pos=3, container_pos=4, hierarchy=HIERARCHY_HOSTS, toml_document=toml_document
    )

    # Insert the "hosts" field right after the first whitespace but before the first comment
    HIERARCHY_NAME = 'name'
    container_insertion_into_toml_source(
        hierarchy=HIERARCHY_NAME, toml_source=toml_document, insertion="Tom Preston-Werner", position=6
    )
    assert toml_document[HIERARCHY_NAME] == "Tom Preston-Werner"
    _inserted_position_test(
        attribute_pos=4, container_pos=6, hierarchy=HIERARCHY_NAME, toml_document=toml_document
    )

    # Insert the "hosts" field right after the first whitespace but before the first comment
    HIERARCHY_RUFF_LINT = 'tool.ruff.lint.cache'
    container_insertion_into_toml_source(
        hierarchy=HIERARCHY_RUFF_LINT, toml_source=toml_document, insertion=True, position=2
    )
    ruff_lint_cache = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_RUFF_LINT, toml_source=toml_document
    )
    assert ruff_lint_cache == True
    _inserted_position_test(
        attribute_pos=1, container_pos=2, hierarchy=HIERARCHY_RUFF_LINT, toml_document=toml_document
    )


def test_insertion_into_toml_c() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_c.toml')

    HIERARCHY_PYDOCTYLE_SELECT = 'tool.ruff.lint.pydocstyle.select'
    attribute_insertion_into_toml_source(
        hierarchy=HIERARCHY_PYDOCTYLE_SELECT, toml_source=toml_document, insertion=["D200"], position=1
    )
    pydocstyle_select = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_PYDOCTYLE_SELECT, toml_source=toml_document
    )
    assert isinstance(pydocstyle_select, items.Array)
    assert pydocstyle_select.unwrap() == ["D200"]
    _inserted_position_test(
        attribute_pos=1, container_pos=1, hierarchy=HIERARCHY_PYDOCTYLE_SELECT, toml_document=toml_document
    )

    HIERARCHY_LINT_EXCLUDE = 'tool.ruff.lint.exclude'
    container_insertion_into_toml_source(
        hierarchy=HIERARCHY_LINT_EXCLUDE, toml_source=toml_document, insertion=["tests/", "docs/conf.py"], position=3
    )
    ruff_lint_exclude = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_LINT_EXCLUDE, toml_source=toml_document
    )
    assert isinstance(ruff_lint_exclude, items.Array)
    assert ruff_lint_exclude.unwrap() == ["tests/", "docs/conf.py"]
    _inserted_position_test(
        attribute_pos=2, container_pos=3, hierarchy=HIERARCHY_LINT_EXCLUDE, toml_document=toml_document
    )