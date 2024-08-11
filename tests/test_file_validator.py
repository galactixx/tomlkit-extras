from pathlib import Path

import pytest
from tomlkit_extras import (
    load_toml_file,
    TOMLDecodingError
)

def test_filepath_load_toml_file() -> None:
    """"""
    _ = load_toml_file(toml_source=r'tests\examples\toml_a.toml')
    _ = load_toml_file(toml_source=r'tests\examples\toml_b.toml')
    _ = load_toml_file(toml_source=r'tests\examples\toml_c.toml')
    _ = load_toml_file(toml_source=r'tests\examples\toml_d.toml')


def test_path_load_toml_file() -> None:
    """"""
    _ = load_toml_file(toml_source=Path(r'tests\examples\toml_a.toml'))
    _ = load_toml_file(toml_source=Path(r'tests\examples\toml_b.toml'))
    _ = load_toml_file(toml_source=Path(r'tests\examples\toml_c.toml'))
    _ = load_toml_file(toml_source=Path(r'tests\examples\toml_d.toml'))


def test_string_load_toml_file() -> None:
    """"""
    _ = load_toml_file(
        toml_source="""
        # this is a document comment

        [project]
        name = "Example Project"

        [details]
        description = "A sample project configuration"
        """
    )
    _ = load_toml_file(
        toml_source="""
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
        """
    )


def test_bytes_load_toml_file() -> None:
    """"""
    _ = load_toml_file(
        toml_source=b"""
        # this is a document comment

        [project]
        name = "Example Project"

        [details]
        description = "A sample project configuration"
        """
    )
    _ = load_toml_file(
        toml_source=b"""
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
        """
    )


def test_bytearray_load_toml_file() -> None:
    """"""
    _ = load_toml_file(
        toml_source=bytearray(b"""
        # this is a document comment

        [project]
        name = "Example Project"

        [details]
        description = "A sample project configuration"
        """
    ))
    _ = load_toml_file(
        toml_source=bytearray(b"""
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
        """
    ))


def test_tomldocument_load_toml_file() -> None:
    """"""
    toml_document_a = load_toml_file(toml_source=r'tests\examples\toml_a.toml')
    _ = load_toml_file(toml_source=toml_document_a)

    toml_document_b = load_toml_file(toml_source=r'tests\examples\toml_b.toml')
    _ = load_toml_file(toml_source=toml_document_b)


def test_dict_load_toml_file() -> None:
    """"""
    _ = load_toml_file(
        toml_source={
            'project': 'Example Project',
            'tool': {
                'ruff': {
                    'line-length': 88,
                    'lint': {
                        'pydocstyle': {'convention': 'numpy'}
                    }
                }
            }
        }
    )
    _ = load_toml_file(
        toml_source={
            'project': 'Example Project',
            'main_table': {
                'name': 'Main Table',
                'description': 'This is the main table containing an array of nested tables.',
                'sub_tables': [
                    {'name': 'Sub Table 1', 'value': 10},
                    {'name': 'Sub Table 2', 'value': 20}
                ]
            }
        }
    )


def test_load_toml_file_invalid() -> None:
    """"""
    with pytest.raises(TOMLDecodingError) as exc_info:
        _ = load_toml_file(toml_source=r'tests\examples\invalid_toml_a.toml')
    assert str(exc_info.value) == 'Key "profile" already exists. at line 8 col 7'

    with pytest.raises(FileNotFoundError) as exc_info:
        _ = load_toml_file(toml_source=r'tests\examples\not_an_existing_file.toml')
    assert str(exc_info.value) == 'If path is passed in as the source, it must link to an existing file'

    with pytest.raises(TypeError) as exc_info:
        _ = load_toml_file(
            toml_source=[{'name': 'Sub Table 1', 'value': 10}, {'name': 'Sub Table 2', 'value': 20}]
        )
    assert str(exc_info.value) == 'Invalid type passed for toml_source argument'