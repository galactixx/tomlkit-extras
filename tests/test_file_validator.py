from pathlib import Path
from typing import Any, Dict

import pytest

from tomlkit_extras import TOMLDecodingError, load_toml_file


@pytest.mark.parametrize(
    "toml_source",
    [
        "./tests/examples/toml_a.toml",
        "./tests/examples/toml_b.toml",
        "./tests/examples/toml_c.toml",
        "./tests/examples/toml_d.toml",
    ],
)
def test_filepath_load_toml_file(toml_source: str) -> None:
    """
    Function to test the functionality of `load_toml_file` when reading
    from a filepath of type string or Path.
    """
    _ = load_toml_file(toml_source=toml_source)
    _ = load_toml_file(toml_source=Path(toml_source))


@pytest.mark.parametrize(
    "toml_source",
    [
        """
        # this is a document comment

        [project]
        name = "Example Project"

        [details]
        description = "A sample project configuration"
        """,
        """
        # This is a sample TOML file with out-of-order tables

        [database]
        server = "192.168.1.1"
        port = 5432
        user = "admin"
        password = "secret"

        [owner]
        name = "Tom Preston-Werner"
        dob = 1979-05-27T07:32:00Z

        [servers.alpha]
        ip = "10.0.0.1"
        role = "frontend"
        # Out-of-order table
        """,
    ],
)
def test_raw_load_toml_file(toml_source: str) -> None:
    """
    Function to test the functionality of `load_toml_file` when reading
    from a string, bytes, and bytearray instance.
    """
    _ = load_toml_file(toml_source=toml_source)
    _ = load_toml_file(toml_source=bytes(toml_source, "utf-8"))
    _ = load_toml_file(toml_source=bytearray(toml_source, "utf-8"))


@pytest.mark.parametrize(
    "toml_source",
    [
        {
            "project": "Example Project",
            "tool": {
                "ruff": {
                    "line-length": 88,
                    "lint": {"pydocstyle": {"convention": "numpy"}},
                }
            },
        },
        {
            "project": "Example Project",
            "main_table": {
                "name": "Main Table",
                "description": "This is the main table containing an array of nested tables.",
                "sub_tables": [
                    {"name": "Sub Table 1", "value": 10},
                    {"name": "Sub Table 2", "value": 20},
                ],
            },
        },
    ],
)
def test_dict_load_toml_file(toml_source: Dict[str, Any]) -> None:
    """
    Function to test the functionality of `load_toml_file` when reading
    from a dictionary.
    """
    _ = load_toml_file(toml_source=toml_source)


def test_load_toml_file_invalid() -> None:
    """Function to test the error handling of `load_toml_file`."""
    with pytest.raises(TOMLDecodingError) as exc_info:
        _ = load_toml_file(toml_source="./tests/examples/invalid_toml_a.toml")
    assert (
        exc_info.value.message == "Issue occured when decoding the TOML source content"
    )

    with pytest.raises(FileNotFoundError) as exc_info:
        _ = load_toml_file(toml_source="./tests/examples/not_an_existing_file.toml")
    assert str(exc_info.value) == (
        "If path is passed in as the source, it must link to an existing file"
    )
