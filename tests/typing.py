from typing import Literal
import sys

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

FixtureFunction: TypeAlias = Literal[
    "load_toml_a", "load_toml_b", "load_toml_c", "load_toml_d", "load_toml_e"
]

FixtureDescriptor: TypeAlias = Literal[
    "toml_a_descriptor", "toml_b_descriptor", "toml_c_descriptor"
]
