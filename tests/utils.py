from tomlkit_extensions.descriptor._descriptor import TOMLDocumentDescriptor
from tomlkit_extensions.hierarchy import Hierarchy

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