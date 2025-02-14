import pytest
from tomlkit import TOMLDocument

from tomlkit_extras import TOMLDocumentDescriptor, load_toml_file


@pytest.fixture(scope="function")
def load_toml_a() -> TOMLDocument:
    """Function-scoped fixture for the toml_a TOML file."""
    return load_toml_file(toml_source="./tests/examples/toml_a.toml")


@pytest.fixture(scope="function")
def load_toml_b() -> TOMLDocument:
    """Function-scoped fixture for the toml_b TOML file."""
    return load_toml_file(toml_source="./tests/examples/toml_b.toml")


@pytest.fixture(scope="function")
def load_toml_c() -> TOMLDocument:
    """Function-scoped fixture for the toml_c TOML file."""
    return load_toml_file(toml_source="./tests/examples/toml_c.toml")


@pytest.fixture(scope="function")
def load_toml_d() -> TOMLDocument:
    """Function-scoped fixture for the toml_d TOML file."""
    return load_toml_file(toml_source="./tests/examples/toml_d.toml")


@pytest.fixture(scope="function")
def load_toml_e() -> TOMLDocument:
    """Function-scoped fixture for the toml_e TOML file."""
    return load_toml_file(toml_source="./tests/examples/toml_e.toml")


@pytest.fixture(scope="function")
def toml_a_descriptor(load_toml_a: TOMLDocument) -> TOMLDocumentDescriptor:
    """Function-scoped fixture for the toml_a `TOMLDocumentDescriptor` instance."""
    document_descriptor = TOMLDocumentDescriptor(toml_source=load_toml_a)
    return document_descriptor


@pytest.fixture(scope="function")
def toml_b_descriptor(load_toml_b: TOMLDocument) -> TOMLDocumentDescriptor:
    """Function-scoped fixture for the toml_b `TOMLDocumentDescriptor` instance."""
    document_descriptor = TOMLDocumentDescriptor(toml_source=load_toml_b)
    return document_descriptor


@pytest.fixture(scope="function")
def toml_c_descriptor(load_toml_c: TOMLDocument) -> TOMLDocumentDescriptor:
    """Function-scoped fixture for the toml_c `TOMLDocumentDescriptor` instance."""
    document_descriptor = TOMLDocumentDescriptor(toml_source=load_toml_c)
    return document_descriptor
