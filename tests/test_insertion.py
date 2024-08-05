from tomlkit import TOMLDocument
from tomlkit_extensions import (
    attribute_insertion_into_toml_source,
    container_insertion_into_toml_source,
    general_insertion_into_toml_source,
    get_attribute_from_toml_source,
    get_positions,
    load_toml_file
)

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
    attribute_pos, container_pos = get_positions(hierarchy=HIERARCHY_PORT, toml_source=toml_document)
    assert attribute_pos == 1
    assert container_pos == 2

    HIERARCHY_TITLE = 'title'

    attribute_insertion_into_toml_source(
        hierarchy=HIERARCHY_TITLE, toml_source=toml_document, insertion="Example TOML Document", position=1
    )
    assert toml_document[HIERARCHY_TITLE] == "Example TOML Document"

    attribute_pos, container_pos = get_positions(hierarchy=HIERARCHY_TITLE, toml_source=toml_document)
    assert attribute_pos == 1
    assert container_pos == 1

    HIERARCHY_HOSTS = 'hosts'

    # Insert right after the comment "# this is a document comment"
    container_insertion_into_toml_source(
        hierarchy=HIERARCHY_HOSTS, toml_source=toml_document, insertion=["alpha", "omega", "beta"], position=2
    )
    assert toml_document[HIERARCHY_HOSTS] == ["alpha", "omega", "beta"]

    attribute_pos, container_pos = get_positions(hierarchy=HIERARCHY_HOSTS, toml_source=toml_document)
    assert attribute_pos == 2
    assert container_pos == 2

    HIERARCHY_PROJECT_VERSION = 'project.version'

    # Perform a general insertion into the project table, should be inserted
    # right after the "name" field
    general_insertion_into_toml_source(
        hierarchy=HIERARCHY_PROJECT_VERSION, toml_source=toml_document, insertion="0.1.0"
    )
    project_version = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_PROJECT_VERSION, toml_source=toml_document
    )
    assert project_version == "0.1.0"

    attribute_pos, container_pos = get_positions(hierarchy=HIERARCHY_PROJECT_VERSION, toml_source=toml_document)
    assert attribute_pos == 2
    assert container_pos == 2

    HIERARCHY_PROJECT_README = 'project.readme'

    # Perform an insertion of field in between the "name" and "version" fields
    attribute_insertion_into_toml_source(
        hierarchy=HIERARCHY_PROJECT_README, toml_source=toml_document, insertion="README.md", position=2
    )
    project_readme = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_PROJECT_README, toml_source=toml_document
    )
    assert project_readme == "README.md"

    attribute_pos, container_pos = get_positions(hierarchy=HIERARCHY_PROJECT_README, toml_source=toml_document)
    assert attribute_pos == 2
    assert container_pos == 2


def test_insertion_into_toml_b() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_b.toml')

    HIERARCHY_TITLE = 'title'

    attribute_insertion_into_toml_source(
        hierarchy=HIERARCHY_TITLE, toml_source=toml_document, insertion="Example TOML Document", position=2
    )
    assert toml_document[HIERARCHY_TITLE] == "Example TOML Document"

    attribute_pos, container_pos = get_positions(hierarchy=HIERARCHY_TITLE, toml_source=toml_document)
    assert attribute_pos == 2
    assert container_pos == 2

    HIERARCHY_HOSTS = 'hosts'

    # Insert the "hosts" field right after the first whitespace but before the first comment
    container_insertion_into_toml_source(
        hierarchy=HIERARCHY_HOSTS, toml_source=toml_document, insertion=["alpha", "omega", "beta"], position=4
    )
    assert toml_document[HIERARCHY_HOSTS] == ["alpha", "omega", "beta"]

    attribute_pos, container_pos = get_positions(hierarchy=HIERARCHY_HOSTS, toml_source=toml_document)
    assert attribute_pos == 3
    assert container_pos == 4

    HIERARCHY_NAME = 'name'

    # Insert the "hosts" field right after the first whitespace but before the first comment
    container_insertion_into_toml_source(
        hierarchy=HIERARCHY_NAME, toml_source=toml_document, insertion="Tom Preston-Werner", position=6
    )
    assert toml_document[HIERARCHY_NAME] == "Tom Preston-Werner"

    attribute_pos, container_pos = get_positions(hierarchy=HIERARCHY_NAME, toml_source=toml_document)
    assert attribute_pos == 4
    assert container_pos == 6

    HIERARCHY_RUFF_LINT = 'tool.ruff.lint.cache'

    # Insert the "hosts" field right after the first whitespace but before the first comment
    container_insertion_into_toml_source(
        hierarchy=HIERARCHY_RUFF_LINT, toml_source=toml_document, insertion=True, position=2
    )
    ruff_lint_cache = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_RUFF_LINT, toml_source=toml_document
    )
    assert ruff_lint_cache == True

    attribute_pos, container_pos = get_positions(hierarchy=HIERARCHY_RUFF_LINT, toml_source=toml_document)
    assert attribute_pos == 1
    assert container_pos == 2


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
    assert pydocstyle_select == ["D200"]

    attribute_pos, container_pos = get_positions(hierarchy=HIERARCHY_PYDOCTYLE_SELECT, toml_source=toml_document)
    assert attribute_pos == 1
    assert container_pos == 1

    HIERARCHY_LINT_EXCLUDE = 'tool.ruff.lint.exclude'

    container_insertion_into_toml_source(
        hierarchy=HIERARCHY_LINT_EXCLUDE, toml_source=toml_document, insertion=["tests/", "docs/conf.py"], position=3
    )
    ruff_lint_exclude = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_LINT_EXCLUDE, toml_source=toml_document
    )
    assert ruff_lint_exclude == ["tests/", "docs/conf.py"]

    attribute_pos, container_pos = get_positions(hierarchy=HIERARCHY_LINT_EXCLUDE, toml_source=toml_document)
    assert attribute_pos == 2
    assert container_pos == 3