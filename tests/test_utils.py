from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    List,
    Optional
)

import pytest
import tomlkit
from tomlkit import items, TOMLDocument

from tomlkit_extras._typing import (
    BodyContainer,
    BodyContainerItem,
    BodyContainerItems
)
from tomlkit_extras._utils import (
    complete_clear_toml_document,
    create_array_of_tables,
    create_toml_document,
    decompose_body_item,
    from_dict_to_toml_document,
    get_container_body,
    _partial_clear_dict_like_toml_item
)
from tests.typing import FixtureFunction

@dataclass(frozen=True)
class BaseClearTestCase:
    """"""
    fixture: FixtureFunction
    num_attributes: int


@dataclass(frozen=True)
class ClearDocumentTestCase(BaseClearTestCase):
    """"""
    pass


@dataclass(frozen=True)
class PartialClearDocumentTestCase(BaseClearTestCase):
    """"""
    pass


@dataclass(frozen=True)
class CreateArrayOTablesTestCase:
    """"""
    arrays: List[Any]
    num_aots: int


@dataclass(frozen=True)
class CreateDocumentTestCase:
    """"""
    hierarchy: str
    table: Dict[str, Any]


@dataclass(frozen=True)
class DecomposeBodyItemTestCase:
    """"""
    key: Optional[items.Key]
    item: items.Item

    @property
    def body_item(self) -> BodyContainerItem:
        """"""
        return (self.key, self.item)


@dataclass(frozen=True)
class GetContainerBodyTestCase:
    """"""
    structure: BodyContainer
    container_body: BodyContainerItems


def table_from_dict(to_table: Dict[str, Any]) -> items.Table:
    """"""
    table: items.Table = tomlkit.table()
    table.update(to_table)
    return table


@pytest.mark.parametrize(
    'test_case',
    [
        ClearDocumentTestCase('load_toml_b', 3),
        ClearDocumentTestCase('load_toml_d', 4)
    ]
)
def test_complete_clear_toml_document(
    test_case: ClearDocumentTestCase, request: pytest.FixtureRequest
) -> None:
    """"""
    toml_document: TOMLDocument = request.getfixturevalue(test_case.fixture)

    assert len(toml_document.values()) == test_case.num_attributes
    complete_clear_toml_document(toml_document=toml_document)
    assert len(toml_document.values()) == 0

    # Ensure that each private attribute is empty
    assert toml_document._map == {}
    assert toml_document._body == []
    assert toml_document._parsed == False
    assert toml_document._table_keys == []


_RAW_TABLE_DICTS: List[Dict[str, Any]] = [
    {'name': 'Sub Table 1', 'value': 10},
    {'name': 'Sub Table 2', 'value': 20}
]


@pytest.mark.parametrize(
    'test_case',
    [
        CreateArrayOTablesTestCase(arrays=_RAW_TABLE_DICTS, num_aots=2),
        CreateArrayOTablesTestCase(
            arrays=[table_from_dict(to_table=table) for table in _RAW_TABLE_DICTS],
            num_aots=2
        ),
        CreateArrayOTablesTestCase(
            arrays=[table_from_dict(to_table=_RAW_TABLE_DICTS[0]), _RAW_TABLE_DICTS[1]],
            num_aots=2
        )
    ]
)
def test_create_array_of_tables(test_case: CreateArrayOTablesTestCase) -> None:
    """"""
    aot_from_dictionaries = create_array_of_tables(tables=test_case.arrays)
    assert isinstance(aot_from_dictionaries, items.AoT)
    assert len(aot_from_dictionaries) == test_case.num_aots


@pytest.mark.parametrize(
    'test_case',
    [
        CreateDocumentTestCase(
            'projects',
            {'project': {'update': {'name': 'Example Project'}}}
        ),
        CreateDocumentTestCase(
            'details',
            {'detail': {'update': {'description': 'A sample project configuration'}}}
        ),
        CreateDocumentTestCase(
            'update.members',
            {'roles': [{'role': 'Developer'}, {'role': 'Designer'}]}
        )
    ]
)
def test_create_toml_document(test_case: CreateDocumentTestCase) -> None:
    """"""
    project_toml_document = create_toml_document(
        hierarchy=test_case.hierarchy, value=test_case.table
    )
    assert isinstance(project_toml_document, TOMLDocument)

    document_unwrapped = project_toml_document.unwrap()
    for level in test_case.hierarchy.split('.'):
        document_unwrapped = document_unwrapped[level]
    
    assert document_unwrapped == test_case.table


@pytest.mark.parametrize(
    'test_case',
    [
        DecomposeBodyItemTestCase(
            tomlkit.key('example_key'), tomlkit.string('example_value')
        ),
        DecomposeBodyItemTestCase(
            tomlkit.key('example.key.here'), tomlkit.integer(42)
        ),
        DecomposeBodyItemTestCase(None, tomlkit.float_(3.14))
    ]
)
def test_decompose_body_item(test_case: DecomposeBodyItemTestCase) -> None:
    """"""
    item_key, toml_item = decompose_body_item(body_item=test_case.body_item)
    assert (
        (
            (isinstance(item_key, str) and test_case.key is not None) or
            (item_key is None and test_case.key is None)
        )
        and isinstance(toml_item, items.Item)
    )


@pytest.mark.parametrize(
    'dictionary',
    [
        {
            'project': 'Example Project',
            'tool': {
                'ruff': {
                    'line-length': 88,
                    'lint': {
                        'pydocstyle': {'convention': 'numpy'}
                    }
                }
            } ,
            'main_table': {
                'name': 'Main Table',
                'description': 'This is the main table containing an array of nested tables.',
                'sub_tables': [
                    {'name': 'Sub Table 1', 'value': 10},
                    {'name': 'Sub Table 2', 'value': 20}
                ]
            }
        },
        {
            'project': 'Example Project',
            'tool': {
                'ruff': {
                    'line-length': 88,
                    'lint': {
                        'pydocstyle': {'convention': 'numpy'}
                    }
                },
                'rye': {
                    'managed': True,
                    'dev-dependencies': [
                        "ruff>=0.4.4",
                        "mypy>=0.812",
                        "sphinx>=3.5",
                        "setuptools>=56.0"
                    ]
                }
            }
        }
    ]
)
def test_from_dict_to_toml_document(dictionary: Dict[str, Any]) -> None:
    """"""
    toml_converted_document = from_dict_to_toml_document(dictionary=dictionary)
    assert isinstance(toml_converted_document, TOMLDocument)
    assert toml_converted_document.unwrap() == dictionary


@pytest.mark.parametrize(
    'test_case',
    [
        GetContainerBodyTestCase(
            from_dict_to_toml_document({'project': 'Example Project', 'profile': 'Tom'}),
            [
                (tomlkit.key('project'), tomlkit.string('Example Project')),
                (tomlkit.key('profile'), tomlkit.string('Tom'))
            ]
        ),
        GetContainerBodyTestCase(
            table_from_dict({'server': '192.168.1.1', 'port': 5432}),
            [
                (tomlkit.key('server'), tomlkit.string('192.168.1.1')),
                (tomlkit.key('port'), tomlkit.integer(5432))
            ]
        )
    ]
)
def test_get_container_body(test_case: GetContainerBodyTestCase) -> None:
    """"""
    container_body = get_container_body(toml_source=test_case.structure)
    assert test_case.container_body == container_body


@pytest.mark.parametrize(
    'test_case',
    [
        PartialClearDocumentTestCase('load_toml_a', 3),
        PartialClearDocumentTestCase('load_toml_b', 3),
        PartialClearDocumentTestCase('load_toml_d', 4)
    ]
)
def test_partial_clear_dict_like_toml_item(
    test_case: PartialClearDocumentTestCase, request: pytest.FixtureRequest
) -> None:
    """"""
    toml_document: TOMLDocument = request.getfixturevalue(test_case.fixture)

    assert len(toml_document.values()) == test_case.num_attributes
    _partial_clear_dict_like_toml_item(toml_source=toml_document)
    assert len(toml_document.values()) == 0