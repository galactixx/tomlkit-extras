import pytest

from tomlkit_extras import TOMLDocumentDescriptor

from tests.utils import (
    AoTDescriptorTestCase,
    ArrayItemsTestCase,
    FieldDescriptorTestCase,
    StyleDescriptorTestCase,
    TableDescriptorTestCase
)

def test_toml_a_statistics(toml_a_document: TOMLDocumentDescriptor) -> None:
    """"""
    assert toml_a_document.number_of_aots == 3
    assert toml_a_document.number_of_arrays == 0
    assert toml_a_document.number_of_comments == 1
    assert toml_a_document.number_of_fields == 7
    assert toml_a_document.number_of_inline_tables == 0
    assert toml_a_document.number_of_tables == 7


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
        )
    ]
)
def test_toml_a_style_descriptors(
    test_case: StyleDescriptorTestCase, toml_a_document: TOMLDocumentDescriptor
) -> None:
    """"""
    styling_descriptors = toml_a_document.get_styling(
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
            'name',
            'project.name',
            4,
            1,
            1,
            'Example Project',
            None,
            False
        ),
        FieldDescriptorTestCase(
            'field',
            'table',
            'description',
            'details.description',
            7,
            1,
            1,
            'A sample project configuration',
            None,
            False
        )
    ]
)
def test_toml_a_field_descriptors(
    test_case: FieldDescriptorTestCase, toml_a_document: TOMLDocumentDescriptor
) -> None:
    """"""
    field_descriptor = toml_a_document.get_field(hierarchy=test_case.hierarchy)
    test_case.validate_descriptor(descriptor=field_descriptor)


@pytest.mark.parametrize(
    'test_case',
    [
        ArrayItemsTestCase(
            hierarchy='members.name',
            test_cases=[
                FieldDescriptorTestCase(
                    'field',
                    'table',
                    'name',
                    'members.name',
                    10,
                    1,
                    1,
                    'Alice',
                    None,
                    True
                ),
                FieldDescriptorTestCase(
                    'field',
                    'table',
                    'name',
                    'members.name',
                    19,
                    1,
                    1,
                    'Bob',
                    None,
                    True
                )
            ]
        )
    ]
)
def test_toml_a_array_field_descriptors(
    test_case: ArrayItemsTestCase, toml_a_document: TOMLDocumentDescriptor
) -> None:
    """"""
    descriptors = toml_a_document.get_field_from_array_of_tables(
        hierarchy=test_case.hierarchy
    )
    assert len(descriptors) == len(test_case.test_cases)

    for idx, field in enumerate(test_case.test_cases):
        field.validate_descriptor(descriptor=descriptors[idx])


@pytest.mark.parametrize(
    'test_case',
    [
        ArrayItemsTestCase(
            hierarchy='members',
            test_cases=[
                TableDescriptorTestCase(
                    'table',
                    'array-of-tables',
                    'members',
                    'members',
                    9,
                    1,
                    1,
                    None,
                    True,
                    1
                ),
                TableDescriptorTestCase(
                    'table',
                    'array-of-tables',
                    'members',
                    'members',
                    18,
                    2,
                    2,
                    None,
                    True,
                    1
                )
            ]
        )
    ]
)
def test_toml_a_array_table_descriptors(
    test_case: ArrayItemsTestCase, toml_a_document: TOMLDocumentDescriptor
) -> None:
    """"""
    descriptors = toml_a_document.get_table_from_array_of_tables(
        hierarchy=test_case.hierarchy
    )
    assert len(descriptors) == len(test_case.test_cases)

    for idx, table in enumerate(test_case.test_cases):
        table.validate_descriptor(descriptor=descriptors[idx])


@pytest.mark.parametrize(
    'test_case',
    [
        ArrayItemsTestCase(
            hierarchy='members',
            test_cases=[
                AoTDescriptorTestCase(
                    'array-of-tables',
                    'document',
                    'members',
                    'members',
                    9,
                    3,
                    5,
                    False,
                    2
                )
            ]
        )
    ]
)
def test_toml_a_array_descriptors(
    test_case: ArrayItemsTestCase, toml_a_document: TOMLDocumentDescriptor
) -> None:
    """"""
    descriptors = toml_a_document.get_array_of_tables(hierarchy=test_case.hierarchy)
    assert len(descriptors) == len(test_case.test_cases)

    for idx, table in enumerate(test_case.test_cases):
        table.validate_descriptor(descriptor=descriptors[idx])