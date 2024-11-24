import copy
from dataclasses import dataclass
from typing import (
    List,
    Optional,
    Tuple
)

import pytest
from tomlkit import items, TOMLDocument
from tomlkit.container import OutOfOrderTableProxy
from tomlkit_extras import (
    contains_out_of_order_tables,
    fix_out_of_order_table,
    fix_out_of_order_tables,
    get_attribute_from_toml_source,
    get_comments
)

from tomlkit_extras._typing import ContainerComment
from tests.typing import FixtureFunction

@dataclass(frozen=True)
class OutOfOrderTestCase:
    """
    Dataclass representing a test case for the `fix_out_of_order_table`
    function
    """
    fixture: FixtureFunction
    hierarchy: Optional[str]
    tables: List[Tuple[str, List[ContainerComment]]]


@pytest.mark.parametrize(
    'fixture', ['load_toml_c', 'load_toml_d', 'load_toml_e']
)
def test_fix_all_out_of_order_tables(
    fixture: FixtureFunction, request: pytest.FixtureRequest
) -> None:
    """Function to test the functionality of `fix_out_of_order_tables`."""
    # Fix the out-order-table from the TOML document in place
    toml_document: TOMLDocument = request.getfixturevalue(fixture)
    toml_document_original = copy.deepcopy(toml_document)
    fix_out_of_order_tables(toml_source=toml_document)

    assert toml_document_original == toml_document
    assert not contains_out_of_order_tables(toml_source=toml_document)


@pytest.mark.parametrize(
    'test_case',
    [
        OutOfOrderTestCase(
            'load_toml_c',
            'tool.ruff',
            [
                (None, [(1, 2, '# this is a tool.ruff comment')]),
                ('lint', [(1, 3, '# this is the first comment for lint table')])
            ]
        ),
        OutOfOrderTestCase(
            'load_toml_d',
            'servers',
            [
                ('alpha', [(1, 3, '# Out-of-order table')]),
                ('beta', [(1, 1, '# Another out-of-order table')])
            ]
        ),
        OutOfOrderTestCase(
            'load_toml_e',
            'project',
            [
                ('details', [(1, 1, '# Awkwardly nested table (sub-section before main section)')]),
                ('details.authors', [(1, 1, '# Nested table here is disjointed')])
            ]
        ),
        OutOfOrderTestCase(
            'load_toml_e',
            'servers',
            [
                (None, [(1, 1, '# This table is nested under servers, but details are spread out')]),
                ('beta', [(1, 3, '# This nesting is awkward')]),
                ('alpha.metadata', [(1, 4, '# Too far from papa')])
            ]
        )
    ]
)
def test_fix_out_of_order_table(
    test_case: OutOfOrderTestCase, request: pytest.FixtureRequest
) -> None:
    """Function to test the functionality of `fix_out_of_order_table`."""
    toml_document: TOMLDocument = request.getfixturevalue(test_case.fixture)
    out_of_order_table = get_attribute_from_toml_source(
        hierarchy=test_case.hierarchy, toml_source=toml_document
    )
    assert isinstance(out_of_order_table, OutOfOrderTableProxy)

    # Fix the out-of-order table and ensure true values/structure has not changed
    fixed_table = fix_out_of_order_table(table=out_of_order_table)
    assert isinstance(fixed_table, items.Table)
    assert fixed_table == out_of_order_table

    # Iterate through each table in test case to ensure comments can be accessed
    for hierarchy, table in test_case.tables:
        table_comments = get_comments(toml_source=fixed_table, hierarchy=hierarchy)
        assert table == table_comments