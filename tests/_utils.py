from __future__ import annotations

from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import (
    Any,
    List,
    Optional
)

from tomlkit_extras import (
    ArrayOfTablesDescriptor,
    CommentDescriptor,
    FieldDescriptor,
    Hierarchy,
    StyleDescriptor,
    TableDescriptor
)

from tomlkit_extras._hierarchy import standardize_hierarchy
from tomlkit_extras._typing import (
    AoTItem,
    FieldItem, 
    ParentItem,
    StyleItem,
    TableItem
)

@dataclass
class ArrayItemsTestCase:
    """"""
    hierarchy: str
    test_cases: List[AbstractTestCase]


@dataclass
class AbstractTestCase(ABC):
    """"""
    def standardize_hierarchy(self, hierarchy: Optional[str]) -> Optional[Hierarchy]:
        """"""
        if hierarchy is not None:
            return standardize_hierarchy(hierarchy=hierarchy)
        else:
            return None

    @abstractmethod
    def validate_descriptor(self, descriptor: Any) -> None:
        """"""
        raise NotImplementedError("This method must be overridden by subclasses")


@dataclass
class StyleDescriptorTestCase(AbstractTestCase):
    """"""
    item_type: StyleItem
    parent_type: ParentItem
    hierarchy: Optional[str]
    line_no: int
    container_position: int
    style: str
    from_aot: bool

    def validate_descriptor(self, descriptor: StyleDescriptor) -> None:
        """"""
        hierarchy = self.standardize_hierarchy(hierarchy=self.hierarchy)

        assert descriptor.item_type == self.item_type
        assert descriptor.parent_type == self.parent_type
        assert descriptor.hierarchy == hierarchy
        assert descriptor.line_no == self.line_no
        assert descriptor.container_position == self.container_position
        assert descriptor.from_aot == self.from_aot
        assert descriptor.style == self.style


@dataclass
class FieldDescriptorTestCase(AbstractTestCase):
    """"""
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
        """"""
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


@dataclass
class TableDescriptorTestCase(AbstractTestCase):
    """"""
    item_type: TableItem
    parent_type: ParentItem
    name: str
    hierarchy: str
    line_no: int
    attribute_position: int
    container_position: int
    comment: Optional[CommentDescriptor]
    from_aot: bool

    # Field test cases that will be iterated through and validated
    # separately
    fields: List[FieldDescriptorTestCase]

    def validate_descriptor(self, descriptor: TableDescriptor) -> None:
        """"""
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

        # Iterate thorugh every field in contained in list of fields expected
        # to be contained within the table
        for field in self.fields:
            field_descriptor = descriptor.fields.get(field.name, None)
            assert field_descriptor is not None
            field.validate_descriptor(descriptor=field_descriptor)
        
        # Ensure the number of fields match (in case there are extra fields
        # in extracted descriptor)
        assert len(self.fields) == descriptor.num_fields


@dataclass
class AoTDescriptorTestCase(AbstractTestCase):
    """"""
    item_type: AoTItem
    parent_type: ParentItem
    name: str
    hierarchy: str
    line_no: int
    attribute_position: int
    container_position: int
    from_aot: bool

    # Table test cases that will be iterated through and validated
    # separately
    tables: List[TableDescriptorTestCase]

    def validate_descriptor(self, descriptor: ArrayOfTablesDescriptor) -> None:
        """"""
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

        # Iterate thorugh every table in contained in list of tables expected
        # to be contained within the array of tables
        for idx, table in enumerate(self.tables):
            table_descriptors = descriptor.tables.get(table.hierarchy, None)
            assert table_descriptors is not None
            table.validate_descriptor(descriptor=table_descriptors[idx])
        
        # Ensure the number of tables match (in case there are extra tables
        # in extracted descriptor)
        assert len(self.tables) == descriptor.num_tables()