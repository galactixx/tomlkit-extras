import pytest

from tomlkit import TOMLDocument
from tomlkit_extras import (
    load_toml_file,
    TOMLDocumentDescriptor
)

@pytest.fixture(scope='session')
def toml_b_document() -> TOMLDocumentDescriptor:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source='./tests/examples/toml_b.toml')
    document_descriptor = TOMLDocumentDescriptor(toml_source=toml_document)
    return document_descriptor