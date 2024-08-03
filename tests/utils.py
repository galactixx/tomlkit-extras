import pytest
from tomlkit import TOMLDocument

from tomlkit_extensions.descriptor._descriptor import TOMLDocumentDescriptor
from tomlkit_extensions.hierarchy import Hierarchy
from tomlkit_extensions.toml.retrieval import get_attribute_from_toml_source
from tomlkit_extensions.exceptions import InvalidHierarchyError

def is_field_instance_test(
    document_descriptor: TOMLDocumentDescriptor, hierarchy: Hierarchy
) -> None:
    """"""
    assert document_descriptor.is_field_instance(hierarchy=hierarchy)
    assert not document_descriptor.is_table_instance(hierarchy=hierarchy)
    assert not document_descriptor.is_array_of_tables_instance(hierarchy=hierarchy)
    

def is_table_instance_test(
    document_descriptor: TOMLDocumentDescriptor, hierarchy: Hierarchy
) -> None:
    """"""
    assert document_descriptor.is_table_instance(hierarchy=hierarchy)
    assert not document_descriptor.is_field_instance(hierarchy=hierarchy)
    assert not document_descriptor.is_array_of_tables_instance(hierarchy=hierarchy)


def is_array_and_table_instance_test(
    document_descriptor: TOMLDocumentDescriptor, hierarchy: Hierarchy
) -> None:
    """"""
    assert document_descriptor.is_table_instance(hierarchy=hierarchy)
    assert document_descriptor.is_array_of_tables_instance(hierarchy=hierarchy)
    assert not document_descriptor.is_field_instance(hierarchy=hierarchy)


def retrieval_error_handling(hierarchy: str, toml_document: TOMLDocument) -> None:
    """"""
    with pytest.raises(InvalidHierarchyError) as exc_info:
        _ = get_attribute_from_toml_source(
            hierarchy=hierarchy, toml_source=toml_document, array_priority=False
        )

    assert str(exc_info.value) == (
        "Hierarchy specified does not exist in TOMLDocument instance"
    )