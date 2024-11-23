import pytest
from tomlkit import TOMLDocument
from tomlkit_extras import (
    load_toml_file,
    TOMLDocumentDescriptor
)

@pytest.fixture(scope='function')
def load_toml_a() -> TOMLDocument:
    """"""
    return load_toml_file(toml_source='./tests/examples/toml_a.toml')


@pytest.fixture(scope='function')
def load_toml_b() -> TOMLDocument:
    """"""
    return load_toml_file(toml_source='./tests/examples/toml_b.toml')


@pytest.fixture(scope='function')
def load_toml_c() -> TOMLDocument:
    """"""
    return load_toml_file(toml_source='./tests/examples/toml_c.toml')


@pytest.fixture(scope='function')
def load_toml_d() -> TOMLDocument:
    """"""
    return load_toml_file(toml_source='./tests/examples/toml_d.toml')


@pytest.fixture(scope='function')
def load_toml_e() -> TOMLDocument:
    """"""
    return load_toml_file(toml_source='./tests/examples/toml_e.toml')


@pytest.fixture(scope='function')
def toml_a_descriptor(load_toml_a: TOMLDocument) -> TOMLDocumentDescriptor:
    """"""
    document_descriptor = TOMLDocumentDescriptor(toml_source=load_toml_a)
    return document_descriptor


@pytest.fixture(scope='function')
def toml_b_descriptor(load_toml_b: TOMLDocument) -> TOMLDocumentDescriptor:
    """"""
    document_descriptor = TOMLDocumentDescriptor(toml_source=load_toml_b)
    return document_descriptor


@pytest.fixture(scope='function')
def toml_c_descriptor(load_toml_c: TOMLDocument) -> TOMLDocumentDescriptor:
    """"""
    document_descriptor = TOMLDocumentDescriptor(toml_source=load_toml_c)
    return document_descriptor