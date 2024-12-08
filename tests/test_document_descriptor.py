from __future__ import annotations

from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import (
    Any,
    List,
    Optional
)

import pytest
from tomlkit_extras import (
    AoTDescriptor,
    CommentDescriptor,
    FieldDescriptor,
    Hierarchy,
    StyleDescriptor,
    TableDescriptor,
    TOMLDocumentDescriptor
)

from tests.typing import FixtureDescriptor
from tomlkit_extras._hierarchy import standardize_hierarchy
from tomlkit_extras._typing import (
    AoTItem,
    FieldItem, 
    ParentItem,
    StyleItem,
    TableItem
)

@dataclass(frozen=True)
class ArrayItemsTestCase:
    """
    Dataclass representing a test case for the `get_field_from_array_of_tables`,
    `get_array_of_tables`, and `get_table_from_array_of_tables` methods.
    """
    fixture: FixtureDescriptor
    hierarchy: str
    test_cases: List[AbstractTestCase]


@dataclass(frozen=True)
class AbstractTestCase(ABC):
    """
    Abstract dataclass representing a generic test case for get methods from the
    `TOMLDocumentDescriptor` class.
    """
    fixture: Optional[FixtureDescriptor]

    def standardize_hierarchy(self, hierarchy: Optional[str]) -> Optional[Hierarchy]:
        """Standardize a hierarchy to `Hierarchy` | None."""
        if hierarchy is not None:
            return standardize_hierarchy(hierarchy=hierarchy)
        else:
            return None

    @abstractmethod
    def validate_descriptor(self, descriptor: Any) -> None:
        """Abstract method to validate the output of method being tested."""
        pass


@dataclass(frozen=True)
class StyleDescriptorTestCase(AbstractTestCase):
    """Dataclass representing a test case for the `get_styling` method."""
    item_type: StyleItem
    parent_type: ParentItem
    hierarchy: Optional[str]
    line_no: int
    container_position: int
    style: str
    from_aot: bool

    def validate_descriptor(self, descriptor: StyleDescriptor) -> None:
        """Validate the output from `get_styling` when tested."""
        hierarchy = self.standardize_hierarchy(hierarchy=self.hierarchy)

        assert descriptor.item_type == self.item_type
        assert descriptor.parent_type == self.parent_type
        assert descriptor.hierarchy == hierarchy
        assert descriptor.line_no == self.line_no
        assert descriptor.container_position == self.container_position
        assert descriptor.from_aot == self.from_aot
        assert descriptor.style == self.style


@dataclass(frozen=True)
class FieldDescriptorTestCase(AbstractTestCase):
    """
    Dataclass representing a test case for the `get_fields` and
    `get_field_from_array_of_tables` methods.
    """
    item_type: FieldItem
    parent_type: ParentItem
    name: str
    hierarchy: str
    line_no: int
    attribute_position: int
    container_position: int
    value: Any
    comment: Optional[CommentDescriptor]
    from_aot: bool

    def validate_descriptor(self, descriptor: FieldDescriptor) -> None:
        """
        Validate the output from the `get_fields` and `get_field_from_array_of_tables`
        methods when tested.
        """
        hierarchy = self.standardize_hierarchy(hierarchy=self.hierarchy)

        assert descriptor.item_type == self.item_type
        assert descriptor.parent_type == self.parent_type
        assert descriptor.name == self.name
        assert descriptor.hierarchy == hierarchy
        assert descriptor.line_no == self.line_no
        assert descriptor.attribute_position == self.attribute_position
        assert descriptor.container_position == self.container_position
        assert descriptor.comment == self.comment
        assert descriptor.from_aot == self.from_aot
        assert descriptor.value == self.value


@dataclass(frozen=True)
class TableDescriptorTestCase(AbstractTestCase):
    """
    Dataclass representing a test case for the `get_tables` and
    `get_table_from_array_of_tables` methods.
    """
    item_type: TableItem
    parent_type: ParentItem
    name: str
    hierarchy: str
    line_no: int
    attribute_position: int
    container_position: int
    comment: Optional[CommentDescriptor]
    from_aot: bool

    # Number of fields expected to be contained in array
    fields: int

    def validate_descriptor(self, descriptor: TableDescriptor) -> None:
        """
        Validate the output from the `get_tables` and `get_table_from_array_of_tables`
        methods when tested.
        """
        hierarchy = self.standardize_hierarchy(hierarchy=self.hierarchy)

        # Ensure all attributes for table descriptor match
        assert descriptor.item_type == self.item_type
        assert descriptor.parent_type == self.parent_type
        assert descriptor.name == self.name
        assert descriptor.hierarchy == hierarchy
        assert descriptor.line_no == self.line_no
        assert descriptor.attribute_position == self.attribute_position
        assert descriptor.container_position == self.container_position
        assert descriptor.comment == self.comment
        assert descriptor.from_aot == self.from_aot
        
        # Ensure the number of fields match (in case there are extra fields
        # in extracted descriptor)
        assert self.fields == descriptor.num_fields


@dataclass(frozen=True)
class AoTDescriptorTestCase(AbstractTestCase):
    """
    Dataclass representing a test case for the `get_array_of_tables` method.
    """
    item_type: AoTItem
    parent_type: ParentItem
    name: str
    hierarchy: str
    line_no: int
    attribute_position: int
    container_position: int
    from_aot: bool

    # Number of tables expected to be contained in array
    tables: int

    def validate_descriptor(self, descriptor: AoTDescriptor) -> None:
        """
        Validate the output from the `get_array_of_tables` method when tested.
        """
        hierarchy = self.standardize_hierarchy(hierarchy=self.hierarchy)

        # Ensure all attributes for array of tables descriptor match
        assert descriptor.item_type == self.item_type
        assert descriptor.parent_type == self.parent_type
        assert descriptor.name == self.name
        assert descriptor.hierarchy == hierarchy
        assert descriptor.line_no == self.line_no
        assert descriptor.attribute_position == self.attribute_position
        assert descriptor.container_position == self.container_position
        assert descriptor.from_aot == self.from_aot

        # Ensure the number of tables match (in case there are extra tables
        # in extracted descriptor)
        assert self.tables == descriptor.num_tables()


@dataclass(frozen=True)
class DescriptorStatisticsTestCase:
    """
    Dataclass representing a test case for the statistics properties.
    """
    fixture: FixtureDescriptor
    num_of_aots: int
    num_of_arrays: int
    num_of_comments: int
    num_of_fields: int
    num_of_inline_tables: int
    num_of_tables: int


@pytest.mark.parametrize(
    'test_case',
    [
        DescriptorStatisticsTestCase('toml_a_descriptor', 3, 0, 1, 7, 0, 7),
        DescriptorStatisticsTestCase('toml_b_descriptor', 1, 0, 4, 9, 1, 5),
        DescriptorStatisticsTestCase('toml_c_descriptor', 0, 1, 6, 4, 1, 3)
    ]
)
def test_toml_statistics(
    test_case: DescriptorStatisticsTestCase, request: pytest.FixtureRequest
) -> None:
    """Function to test the functionality of the statistics properties."""
    descriptor: TOMLDocumentDescriptor = request.getfixturevalue(test_case.fixture)

    # Check to ensure all statistics in descriptor are accurate
    assert descriptor.number_of_aots == test_case.num_of_aots
    assert descriptor.number_of_arrays == test_case.num_of_arrays
    assert descriptor.number_of_comments == test_case.num_of_comments
    assert descriptor.number_of_fields == test_case.num_of_fields
    assert descriptor.number_of_inline_tables == test_case.num_of_inline_tables
    assert descriptor.number_of_tables == test_case.num_of_tables


@pytest.mark.parametrize(
    'test_case',
    [
        StyleDescriptorTestCase(
            'toml_a_descriptor',
            'comment',
            'document',
            None,
            1,
            1,
            '# this is a document comment',
            False
        ),
        StyleDescriptorTestCase(
            'toml_b_descriptor',
            'comment',
            'document',
            None,
            4,
            3,
            '# this is a document comment',
            False
        ),
        StyleDescriptorTestCase(
            'toml_b_descriptor',
            'comment',
            'table',
            'tool.ruff.lint',
            10,
            1,
            '# this is the first comment for lint table',
            False
        ),
        StyleDescriptorTestCase(
            'toml_b_descriptor',
            'comment',
            'table',
            'tool.ruff.lint',
            11,
            2,
            '# this is the second comment for lint table',
            False
        ),
        StyleDescriptorTestCase(
            'toml_c_descriptor',
            'comment',
            'document',
            None,
            1,
            1,
            '# this is a document comment',
            False
        ),
        StyleDescriptorTestCase(
            'toml_c_descriptor',
            'comment',
            'table',
            'tool.ruff.lint',
            11,
            3,
            '# this is the first comment for lint table',
            False
        ),
        StyleDescriptorTestCase(
            'toml_c_descriptor',
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
def test_toml_style_descriptor(
    test_case: StyleDescriptorTestCase, request: pytest.FixtureRequest
) -> None:
    """Function to test the functionality of `get_styling`."""
    toml_descriptor: TOMLDocumentDescriptor = request.getfixturevalue(test_case.fixture)
    styling_descriptors = toml_descriptor.get_stylings(
        styling=test_case.style, hierarchy=test_case.hierarchy
    )
    assert len(styling_descriptors) == 1

    test_case.validate_descriptor(descriptor=styling_descriptors[0])


@pytest.mark.parametrize(
    'test_case',
    [
        FieldDescriptorTestCase(
            'toml_a_descriptor',
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
            'toml_a_descriptor',
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
        ),
        FieldDescriptorTestCase(
            'toml_b_descriptor',
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
            'toml_b_descriptor',
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
            'toml_b_descriptor',
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
            'toml_b_descriptor',
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
            'toml_b_descriptor',
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
        ),
        FieldDescriptorTestCase(
            'toml_c_descriptor',
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
            'toml_c_descriptor',
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
            'toml_c_descriptor',
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
            'toml_c_descriptor',
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
            'toml_c_descriptor',
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
def test_toml_field_descriptor(
    test_case: FieldDescriptorTestCase, request: pytest.FixtureRequest
) -> None:
    """Function to test the functionality of `get_field`."""
    toml_descriptor: TOMLDocumentDescriptor = request.getfixturevalue(test_case.fixture)
    field_descriptor = toml_descriptor.get_field(hierarchy=test_case.hierarchy)
    test_case.validate_descriptor(descriptor=field_descriptor)


@pytest.mark.parametrize(
    'test_case',
    [
        TableDescriptorTestCase(
            'toml_b_descriptor',
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
            'toml_b_descriptor',
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
            'toml_b_descriptor',
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
        ),
        TableDescriptorTestCase(
            'toml_c_descriptor',
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
            'toml_c_descriptor',
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
            'toml_c_descriptor',
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
def test_toml_table_descriptor(
    test_case: TableDescriptorTestCase, request: pytest.FixtureRequest
) -> None:
    """Function to test the functionality of `get_table`."""
    toml_descriptor: TOMLDocumentDescriptor = request.getfixturevalue(test_case.fixture)
    table_descriptor = toml_descriptor.get_table(hierarchy=test_case.hierarchy)
    test_case.validate_descriptor(descriptor=table_descriptor)


@pytest.mark.parametrize(
    'test_case',
    [
        ArrayItemsTestCase(
            'toml_a_descriptor',
            'members.name',
            [
                FieldDescriptorTestCase(
                    None,
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
                    None,
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
        ),
        ArrayItemsTestCase(
            'toml_b_descriptor',
            'main_table.sub_tables.name',
            [
                FieldDescriptorTestCase(
                    None,
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
                    None,
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
            'toml_b_descriptor',
            'main_table.sub_tables.value',
            [
                FieldDescriptorTestCase(
                    None,
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
                    None,
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
def test_toml_array_field_descriptor(
    test_case: ArrayItemsTestCase, request: pytest.FixtureRequest
) -> None:
    """Function to test the functionality of `get_field_from_array_of_tables`."""
    toml_descriptor: TOMLDocumentDescriptor = request.getfixturevalue(test_case.fixture)
    descriptors = toml_descriptor.get_field_from_aot(
        hierarchy=test_case.hierarchy
    )
    assert len(descriptors) == len(test_case.test_cases)

    for idx, field in enumerate(test_case.test_cases):
        field.validate_descriptor(descriptor=descriptors[idx])


@pytest.mark.parametrize(
    'test_case',
    [
        ArrayItemsTestCase(
            'toml_a_descriptor',
            'members',
            [
                TableDescriptorTestCase(
                    None,
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
                    None,
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
        ),
        ArrayItemsTestCase(
            'toml_b_descriptor',
            'main_table.sub_tables',
            [
                TableDescriptorTestCase(
                    None,
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
                    None,
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
def test_toml_array_table_descriptor(
    test_case: ArrayItemsTestCase, request: pytest.FixtureRequest
) -> None:
    """Function to test the functionality of `get_table_from_array_of_tables`."""
    toml_descriptor: TOMLDocumentDescriptor = request.getfixturevalue(test_case.fixture)
    descriptors = toml_descriptor.get_table_from_aot(
        hierarchy=test_case.hierarchy
    )
    assert len(descriptors) == len(test_case.test_cases)

    for idx, table in enumerate(test_case.test_cases):
        table.validate_descriptor(descriptor=descriptors[idx])


@pytest.mark.parametrize(
    'test_case',
    [
        ArrayItemsTestCase(
            'toml_a_descriptor',
            'members',
            [
                AoTDescriptorTestCase(
                    None,
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
        ),
        ArrayItemsTestCase(
            'toml_b_descriptor',
            'main_table.sub_tables',
            [
                AoTDescriptorTestCase(
                    None,
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
def test_toml_array_descriptor(
    test_case: ArrayItemsTestCase, request: pytest.FixtureRequest
) -> None:
    """Function to test the functionality of `get_array_of_tables`."""
    toml_descriptor: TOMLDocumentDescriptor = request.getfixturevalue(test_case.fixture)
    descriptors = toml_descriptor.get_aot(hierarchy=test_case.hierarchy)
    assert len(descriptors) == len(test_case.test_cases)

    for idx, table in enumerate(test_case.test_cases):
        table.validate_descriptor(descriptor=descriptors[idx])