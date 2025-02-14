from typing import Literal, TypeAlias
import sys

_IS_PY_3_10 = sys.version_info >= (3, 10)

if _IS_PY_3_10:
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

FixtureFunction: TypeAlias = Literal[
    "load_toml_a", "load_toml_b", "load_toml_c", "load_toml_d", "load_toml_e"
]

FixtureDescriptor: TypeAlias = Literal[
    "toml_a_descriptor", "toml_b_descriptor", "toml_c_descriptor"
]
