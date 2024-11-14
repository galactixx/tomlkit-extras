import pytest

from tomlkit_extras import (
    CommentDescriptor,
    TOMLDocumentDescriptor
)

from tests.utils import (
    AoTDescriptorTestCase,
    ArrayItemsTestCase,
    FieldDescriptorTestCase,
    StyleDescriptorTestCase,
    TableDescriptorTestCase
)

def test_toml_b_statistics(toml_b_document: TOMLDocumentDescriptor) -> None:
    """"""
    assert toml_b_document.number_of_aots == 1
    assert toml_b_document.number_of_arrays == 0
    assert toml_b_document.number_of_comments == 4
    assert toml_b_document.number_of_fields == 9
    assert toml_b_document.number_of_inline_tables == 1
    assert toml_b_document.number_of_tables == 5


@pytest.mark.parametrize(
    'test_case',
    [
        StyleDescriptorTestCase(
            'comment',
            'document',
            None,
            4,
            3,
            '# this is a document comment',
            False
        ),
        StyleDescriptorTestCase(
            'comment',
            'table',
            'tool.ruff.lint',
            10,
            1,
            '# this is the first comment for lint table',
            False
        ),
        StyleDescriptorTestCase(
            'comment',
            'table',
            'tool.ruff.lint',
            11,
            2,
            '# this is the second comment for lint table',
            False
        )
    ]
)
def test_toml_b_style_descriptors(
    test_case: StyleDescriptorTestCase, toml_b_document: TOMLDocumentDescriptor
) -> None:
    """"""
    styling_descriptors = toml_b_document.get_styling(
        styling=test_case.style, hierarchy=test_case.hierarchy
    )
    assert len(styling_descriptors) == 1

    test_case.validate_descriptor(descriptor=styling_descriptors[0])


@pytest.mark.parametrize(
    'test_case',
    [
        FieldDescriptorTestCase(
            'field',
            'table',
            'line-length',
            'tool.ruff.line-length',
            7,
            1,
            1,
            88,
            None,
            False
        ),
        FieldDescriptorTestCase(
            'field',
            'inline-table',
            'convention',
            'tool.ruff.lint.pydocstyle.convention',
            12,
            1,
            2,
            'numpy',
            None,
            False
        ),
        FieldDescriptorTestCase(
            'field',
            'table',
            'name',
            'main_table.name',
            15,
            1,
            1,
            'Main Table',
            None,
            False
        ),
        FieldDescriptorTestCase(
            'field',
            'table',
            'description',
            'main_table.description',
            16,
            2,
            2,
            'This is the main table containing an array of nested tables.',
            None,
            False
        ),
        FieldDescriptorTestCase(
            'field',
            'document',
            'project',
            'project',
            1,
            1,
            1,
            'Example Project',
            None,
            False
        )
    ]
)
def test_toml_b_field_descriptors(
    test_case: FieldDescriptorTestCase, toml_b_document: TOMLDocumentDescriptor
) -> None:
    """"""
    field_descriptor = toml_b_document.get_field(hierarchy=test_case.hierarchy)
    test_case.validate_descriptor(descriptor=field_descriptor)


@pytest.mark.parametrize(
    'test_case',
    [
        TableDescriptorTestCase(
            'table',
            'super-table',
            'ruff',
            'tool.ruff',
            6,
            1,
            1,
            CommentDescriptor(
                comment='# this is a tool.ruff comment', line_no=6
            ),
            False,
            1
        ),
        TableDescriptorTestCase(
            'inline-table',
            'table',
            'pydocstyle',
            'tool.ruff.lint.pydocstyle',
            12,
            1,
            3,
            None,
            False,
            1
        ),
        TableDescriptorTestCase(
            'table',
            'document',
            'main_table',
            'main_table',
            14,
            3,
            6,
            None,
            False,
            2
        )
    ]
)
def test_toml_b_table_descriptors(
    test_case: TableDescriptorTestCase, toml_b_document: TOMLDocumentDescriptor
) -> None:
    """"""
    table_descriptor = toml_b_document.get_table(hierarchy=test_case.hierarchy)
    test_case.validate_descriptor(descriptor=table_descriptor)


@pytest.mark.parametrize(
    'test_case',
    [
        ArrayItemsTestCase(
            hierarchy='main_table.sub_tables.name',
            test_cases=[
                FieldDescriptorTestCase(
                    'field',
                    'table',
                    'name',
                    'main_table.sub_tables.name',
                    19,
                    1,
                    1,
                    'Sub Table 1',
                    None,
                    True
                ),
                FieldDescriptorTestCase(
                    'field',
                    'table',
                    'name',
                    'main_table.sub_tables.name',
                    23,
                    1,
                    1,
                    'Sub Table 2',
                    None,
                    True
                )
            ]
        ),
        ArrayItemsTestCase(
            hierarchy='main_table.sub_tables.value',
            test_cases=[
                FieldDescriptorTestCase(
                    'field',
                    'table',
                    'value',
                    'main_table.sub_tables.value',
                    20,
                    2,
                    2,
                    10,
                    None,
                    True
                ),
                FieldDescriptorTestCase(
                    'field',
                    'table',
                    'value',
                    'main_table.sub_tables.value',
                    24,
                    2,
                    2,
                    20,
                    None,
                    True
                )
            ]
        )
    ]
)
def test_toml_a_array_field_descriptors(
    test_case: ArrayItemsTestCase, toml_b_document: TOMLDocumentDescriptor
) -> None:
    """"""
    descriptors = toml_b_document.get_field_from_array_of_tables(
        hierarchy=test_case.hierarchy
    )
    assert len(descriptors) == len(test_case.test_cases)

    for idx, field in enumerate(test_case.test_cases):
        field.validate_descriptor(descriptor=descriptors[idx])


@pytest.mark.parametrize(
    'test_case',
    [
        ArrayItemsTestCase(
            hierarchy='main_table.sub_tables',
            test_cases=[
                TableDescriptorTestCase(
                    'table',
                    'array-of-tables',
                    'sub_tables',
                    'main_table.sub_tables',
                    18,
                    1,
                    1,
                    None,
                    True,
                    2
                ),
                TableDescriptorTestCase(
                    'table',
                    'array-of-tables',
                    'sub_tables',
                    'main_table.sub_tables',
                    22,
                    2,
                    2,
                    None,
                    True,
                    2
                )
            ]
        )
    ]
)
def test_toml_a_array_table_descriptors(
    test_case: ArrayItemsTestCase, toml_b_document: TOMLDocumentDescriptor
) -> None:
    """"""
    descriptors = toml_b_document.get_table_from_array_of_tables(
        hierarchy=test_case.hierarchy
    )
    assert len(descriptors) == len(test_case.test_cases)

    for idx, table in enumerate(test_case.test_cases):
        table.validate_descriptor(descriptor=descriptors[idx])


@pytest.mark.parametrize(
    'test_case',
    [
        ArrayItemsTestCase(
            hierarchy='main_table.sub_tables',
            test_cases=[
                AoTDescriptorTestCase(
                    'array-of-tables',
                    'table',
                    'sub_tables',
                    'main_table.sub_tables',
                    18,
                    3,
                    4,
                    False,
                    2
                )
            ]
        )
    ]
)
def test_toml_a_array_descriptors(
    test_case: ArrayItemsTestCase, toml_b_document: TOMLDocumentDescriptor
) -> None:
    """"""
    descriptors = toml_b_document.get_array_of_tables(hierarchy=test_case.hierarchy)
    assert len(descriptors) == len(test_case.test_cases)

    for idx, table in enumerate(test_case.test_cases):
        table.validate_descriptor(descriptor=descriptors[idx])
        