import copy

import pytest
from tomlkit import TOMLDocument
from tomlkit_extras import (
    load_toml_file,
    TOMLDocumentDescriptor
)

@pytest.fixture(scope='session')
def load_toml_a() -> TOMLDocument:
    """"""
    return load_toml_file(toml_source='./tests/examples/toml_a.toml')


@pytest.fixture(scope='session')
def load_toml_b() -> TOMLDocument:
    """"""
    return load_toml_file(toml_source='./tests/examples/toml_b.toml')


@pytest.fixture(scope='session')
def load_toml_c() -> TOMLDocument:
    """"""
    return load_toml_file(toml_source='./tests/examples/toml_c.toml')


@pytest.fixture(scope='module')
def load_toml_a_module(load_toml_a: TOMLDocument) -> TOMLDocument:
    """"""
    return copy.deepcopy(load_toml_a)


@pytest.fixture(scope='module')
def load_toml_b_module(load_toml_b: TOMLDocument) -> TOMLDocument:
    """"""
    return copy.deepcopy(load_toml_b)


@pytest.fixture(scope='module')
def load_toml_c_module(load_toml_c: TOMLDocument) -> TOMLDocument:
    """"""
    return copy.deepcopy(load_toml_c)


@pytest.fixture(scope='session')
def toml_a_document(load_toml_a: TOMLDocument) -> TOMLDocumentDescriptor:
    """"""
    document_descriptor = TOMLDocumentDescriptor(toml_source=load_toml_a)
    return document_descriptor


@pytest.fixture(scope='session')
def toml_b_document(load_toml_b: TOMLDocument) -> TOMLDocumentDescriptor:
    """"""
    document_descriptor = TOMLDocumentDescriptor(toml_source=load_toml_b)
    return document_descriptor


@pytest.fixture(scope='session')
def toml_c_document(load_toml_c: TOMLDocument) -> TOMLDocumentDescriptor:
    """"""
    document_descriptor = TOMLDocumentDescriptor(toml_source=load_toml_c)
    return document_descriptor