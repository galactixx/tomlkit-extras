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
    detect_out_of_order_tables,
    fix_out_of_order_table,
    fix_out_of_order_tables,
    get_attribute_from_toml_source,
    get_comments,
    load_toml_file
)

from tomlkit_extras._typing import ContainerComment

@pytest.fixture(scope='function')
def toml_c_document() -> TOMLDocument:
    """"""
    return load_toml_file(toml_source='./tests/examples/toml_c.toml')


@pytest.fixture(scope='function')
def toml_d_document() -> TOMLDocument:
    """"""
    return load_toml_file(toml_source='./tests/examples/toml_d.toml')


@pytest.fixture(scope='function')
def toml_e_document() -> TOMLDocument:
    """"""
    return load_toml_file(toml_source='./tests/examples/toml_e.toml')


@dataclass(frozen=True)
class OutOfOrderTestCase:
    """"""
    hierarchy: Optional[str]
    tables: List[Tuple[str, List[ContainerComment]]]

    def validate_comments_access(self, fixed_table: items.Table) -> None:
        """
        # Iterate through each table in test case to ensure comments can be accessed.
        """
        # Iterate through each table in test case to ensure comments can be accessed
        for hierarchy, table in self.tables:
            table_comments = get_comments(toml_source=fixed_table, hierarchy=hierarchy)
            assert table == table_comments


def validate_out_of_order_table(hierarchy: str, toml_document: TOMLDocument) -> items.Table:
    """
    Fix the out-of-order table and ensure true values/structure has not changed.
    """
    out_of_order_table = get_attribute_from_toml_source(
        hierarchy=hierarchy, toml_source=toml_document
    )
    assert isinstance(out_of_order_table, OutOfOrderTableProxy)

    # Fix the out-of-order table and ensure true values/structure has not changed
    fixed_order_table = fix_out_of_order_table(table=out_of_order_table)
    assert isinstance(fixed_order_table, items.Table)
    assert fixed_order_table == out_of_order_table

    return fixed_order_table


def validate_out_of_order_tables(toml_document: TOMLDocument) -> None:
    """# Fix the out-order-table from the TOML document in place."""
    # Fix the out-order-table from the TOML document in place
    toml_document_original = copy.deepcopy(toml_document)
    fix_out_of_order_tables(toml_source=toml_document)

    assert toml_document_original == toml_document
    assert not detect_out_of_order_tables(toml_source=toml_document)


def test_fix_all_out_of_order_toml_c(toml_c_document: TOMLDocument) -> None:
    """"""
    validate_out_of_order_tables(toml_document=toml_c_document)


def test_fix_all_out_of_order_toml_d(toml_d_document: TOMLDocument) -> None:
    """"""
    validate_out_of_order_tables(toml_document=toml_d_document)


def test_fix_all_out_of_order_toml_e(toml_e_document: TOMLDocument) -> None:
    """"""
    validate_out_of_order_tables(toml_document=toml_e_document)


@pytest.mark.parametrize(
    'test_case',
    [
        OutOfOrderTestCase(
            hierarchy='tool.ruff',
            tables=[
                (None, [(1, 2, '# this is a tool.ruff comment')]),
                ('lint', [(1, 3, '# this is the first comment for lint table')])
            ]
        )
    ]
)
def test_fix_out_of_order_toml_c(
    test_case: OutOfOrderTestCase, toml_c_document: TOMLDocument
) -> None:
    """"""
    fixed_order_table = validate_out_of_order_table(
        hierarchy=test_case.hierarchy, toml_document=toml_c_document
    )
    test_case.validate_comments_access(fixed_table=fixed_order_table)


@pytest.mark.parametrize(
    'test_case',
    [
        OutOfOrderTestCase(
            hierarchy='servers',
            tables=[
                ('alpha', [(1, 3, '# Out-of-order table')]),
                ('beta', [(1, 1, '# Another out-of-order table')])
            ]
        )
    ]
)
def test_fix_out_of_order_toml_d(
    test_case: OutOfOrderTestCase, toml_d_document: TOMLDocument
) -> None:
    """"""
    fixed_order_table = validate_out_of_order_table(
        hierarchy=test_case.hierarchy, toml_document=toml_d_document
    )
    test_case.validate_comments_access(fixed_table=fixed_order_table)


@pytest.mark.parametrize(
    'test_case',
    [
        OutOfOrderTestCase(
            hierarchy='project',
            tables=[
                ('details', [(1, 1, '# Awkwardly nested table (sub-section before main section)')]),
                ('details.authors', [(1, 1, '# Nested table here is disjointed')])
            ]
        ),
        OutOfOrderTestCase(
            hierarchy='servers',
            tables=[
                (None, [(1, 1, '# This table is nested under servers, but details are spread out')]),
                ('beta', [(1, 3, '# This nesting is awkward')]),
                ('alpha.metadata', [(1, 4, '# Too far from papa')])
            ]
        )
    ]
)
def test_fix_out_of_order_toml_e(
    test_case: OutOfOrderTestCase, toml_e_document: TOMLDocument
) -> None:
    """"""
    fixed_order_table = validate_out_of_order_table(
        hierarchy=test_case.hierarchy, toml_document=toml_e_document
    )
    test_case.validate_comments_access(fixed_table=fixed_order_table)