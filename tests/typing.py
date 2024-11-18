from typing import (
    Literal,
    TypeAlias
)

FixtureModule: TypeAlias = Literal[
    'load_toml_a_module',
    'load_toml_b_module',
    'load_toml_c_module'
]

FixtureSession: TypeAlias = Literal[
    'load_toml_a', 'load_toml_b', 'load_toml_c'
]

FixtureDescriptor: TypeAlias = Literal[
    'toml_a_document', 'toml_b_document', 'toml_c_document'
]