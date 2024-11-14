import pytest

from tomlkit_extras import TOMLDocumentDescriptor

from tests.utils import (
    FieldDescriptorTestCase,
    StyleDescriptorTestCase,
    TableDescriptorTestCase
)

def test_toml_c_statistics(toml_c_document: TOMLDocumentDescriptor) -> None:
    """"""
    assert toml_c_document.number_of_aots == 0
    assert toml_c_document.number_of_arrays == 1
    assert toml_c_document.number_of_comments == 6
    assert toml_c_document.number_of_fields == 4
    assert toml_c_document.number_of_inline_tables == 1
    assert toml_c_document.number_of_tables == 3


@pytest.mark.parametrize(
    'test_case',
    [
        StyleDescriptorTestCase(
            'comment',
            'document',
            None,
            1,
            1,
            '# this is a document comment',
            False
        ),
        StyleDescriptorTestCase(
            'comment',
            'table',
            'tool.ruff.lint',
            11,
            3,
            '# this is the first comment for lint table',
            False
        ),
        StyleDescriptorTestCase(
            'comment',
            'table',
            'tool.ruff',
            15,
            2,
            '# this is a tool.ruff comment',
            False
        )
    ]
)
def test_toml_c_style_descriptors(
    test_case: StyleDescriptorTestCase, toml_c_document: TOMLDocumentDescriptor
) -> None:
    """"""
    styling_descriptors = toml_c_document.get_styling(
        styling=test_case.style, hierarchy=test_case.hierarchy
    )
    assert len(styling_descriptors) == 1

    test_case.validate_descriptor(descriptor=styling_descriptors[0])


@pytest.mark.parametrize(
    'test_case',
    [
        FieldDescriptorTestCase(
            'field',
            'document',
            'project',
            'project',
            3,
            1,
            3,
            'Example Project',
            None,
            False
        ),
        FieldDescriptorTestCase(
            'field',
            'inline-table',
            'convention',
            'tool.ruff.lint.pydocstyle.convention',
            9,
            1,
            2,
            'numpy',
            None,
            False
        ),
        FieldDescriptorTestCase(
            'field',
            'table',
            'line-length',
            'tool.ruff.line-length',
            14,
            1,
            1,
            88,
            None,
            False
        ),
        FieldDescriptorTestCase(
            'field',
            'table',
            'managed',
            'tool.rye.managed',
            20,
            1,
            1,
            True,
            None,
            False
        ),
        FieldDescriptorTestCase(
            'array',
            'table',
            'dev-dependencies',
            'tool.rye.dev-dependencies',
            21,
            2,
            2,
            [
                'ruff>=0.4.4',
                'mypy>=0.812',
                'sphinx>=3.5',
                'setuptools>=56.0'
            ],
            None,
            False
        )
    ]
)
def test_toml_c_field_descriptors(
    test_case: FieldDescriptorTestCase, toml_c_document: TOMLDocumentDescriptor
) -> None:
    """"""
    field_descriptor = toml_c_document.get_field(hierarchy=test_case.hierarchy)
    test_case.validate_descriptor(descriptor=field_descriptor)


@pytest.mark.parametrize(
    'test_case',
    [
        TableDescriptorTestCase(
            'inline-table',
            'table',
            'pydocstyle',
            'tool.ruff.lint.pydocstyle',
            9,
            1,
            1,
            None,
            False,
            1
        ),
        TableDescriptorTestCase(
            'table',
            'super-table',
            'ruff',
            'tool.ruff',
            13,
            2,
            2,
            None,
            False,
            1
        ),
        TableDescriptorTestCase(
            'table',
            'super-table',
            'rye',
            'tool.rye',
            19,
            3,
            3,
            None,
            False,
            2
        )
    ]
)
def test_toml_b_table_descriptors(
    test_case: TableDescriptorTestCase, toml_c_document: TOMLDocumentDescriptor
) -> None:
    """"""
    table_descriptor = toml_c_document.get_table(hierarchy=test_case.hierarchy)
    test_case.validate_descriptor(descriptor=table_descriptor)


