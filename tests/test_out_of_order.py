import copy
from typing import Union

from tomlkit import items, TOMLDocument
from tomlkit.container import OutOfOrderTableProxy
from tomlkit_extras import (
    fix_out_of_order_table,
    fix_out_of_order_tables,
    get_attribute_from_toml_source,
    get_comments,
    load_toml_file
)

VALID_TYPES = (TOMLDocument, items.Table, items.AoT, OutOfOrderTableProxy)

def _detect_any_out_of_order_tables(
    toml_source: Union[TOMLDocument, items.Table, items.AoT, OutOfOrderTableProxy]
) -> bool:
    """"""
    if isinstance(toml_source, (TOMLDocument, items.Table)):
        return any(
             _detect_any_out_of_order_tables(toml_source=document_value)
            for _, document_value in toml_source.items() if isinstance(document_value, VALID_TYPES)
        )
    elif isinstance(toml_source, items.AoT):
        return any(
            _detect_any_out_of_order_tables(toml_source=aot_table)
            for aot_table in toml_source
        )
    else:
        return True


def test_out_of_order_toml_c() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_c.toml')

    HIERARCHY_TOOL_RUFF = 'tool.ruff'
    out_of_order_table = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_TOOL_RUFF, toml_source=toml_document
    )
    assert isinstance(out_of_order_table, OutOfOrderTableProxy)

    # Fix the out-of-order table and ensure true values/structure has not changed
    fixed_order_table = fix_out_of_order_table(table=out_of_order_table)
    assert isinstance(fixed_order_table, items.Table)
    assert fixed_order_table == out_of_order_table

    # Now that the values have been checked, ensure that the comments for each table
    # are as expected, and have remained unchanged/altered
    tool_ruff_table_comments = get_comments(toml_source=fixed_order_table)
    assert tool_ruff_table_comments == [(2, '# this is a tool.ruff comment')]

    # Check for the nested tool.ruff.lint table as well
    tool_ruff_lint_table_comments = get_comments(toml_source=fixed_order_table, hierarchy='lint')
    assert tool_ruff_lint_table_comments == [(3, '# this is the first comment for lint table')]

    # Fix the out-order-table from the TOML document in place
    toml_document_original = copy.deepcopy(toml_document)
    fix_out_of_order_tables(toml_source=toml_document)

    assert toml_document_original == toml_document
    assert not _detect_any_out_of_order_tables(toml_source=toml_document)


def test_out_of_order_toml_d() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_d.toml')

    HIERARCHY_SERVERS = 'servers'
    out_of_order_table = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_SERVERS, toml_source=toml_document
    )
    assert isinstance(out_of_order_table, OutOfOrderTableProxy)

    # Fix the out-of-order table and ensure true values/structure has not changed
    fixed_order_table = fix_out_of_order_table(table=out_of_order_table)
    assert isinstance(fixed_order_table, items.Table)
    assert fixed_order_table == out_of_order_table

    # Now that the values have been checked, ensure that the comments for each table
    # are as expected, and have remained unchanged/altered
    servers_alpha_comments = get_comments(toml_source=fixed_order_table, hierarchy='alpha')
    assert servers_alpha_comments == [(3, '# Out-of-order table')]

    servers_beta_comments = get_comments(toml_source=fixed_order_table, hierarchy='beta')
    assert servers_beta_comments == [(1, '# Another out-of-order table')]

    # Fix the out-order-table from the TOML document in place
    toml_document_original = copy.deepcopy(toml_document)
    fix_out_of_order_tables(toml_source=toml_document)

    assert toml_document_original == toml_document
    assert not _detect_any_out_of_order_tables(toml_source=toml_document)


def test_out_of_order_toml_e() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_e.toml')

    HIERARCHY_PROJECT = 'project'
    project_out_of_order_table = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_PROJECT, toml_source=toml_document
    )
    assert isinstance(project_out_of_order_table, OutOfOrderTableProxy)

    # Fix the out-of-order table and ensure true values/structure has not changed
    project_fixed_order_table = fix_out_of_order_table(table=project_out_of_order_table)
    assert isinstance(project_fixed_order_table, items.Table)
    assert project_fixed_order_table == project_out_of_order_table

    HIERARCHY_SERVERS = 'servers'
    servers_out_of_order_table = get_attribute_from_toml_source(
        hierarchy=HIERARCHY_SERVERS, toml_source=toml_document
    )
    assert isinstance(servers_out_of_order_table, OutOfOrderTableProxy)

    # Fix the out-of-order table and ensure true values/structure has not changed
    servers_fixed_order_table = fix_out_of_order_table(table=servers_out_of_order_table)
    assert isinstance(servers_fixed_order_table, items.Table)
    assert servers_fixed_order_table == servers_out_of_order_table

    # Now that the values have been checked, ensure that the comments for each table
    # are as expected, and have remained unchanged/altered
    project_details_comments = get_comments(toml_source=project_fixed_order_table, hierarchy='details')
    assert project_details_comments == [(1, '# Awkwardly nested table (sub-section before main section)')]

    project_authors_comments = get_comments(toml_source=project_fixed_order_table, hierarchy='details.authors')
    assert project_authors_comments == [(1, '# Nested table here is disjointed')]

    servers_comments = get_comments(toml_source=servers_fixed_order_table)
    assert servers_comments == [(1, '# This table is nested under servers, but details are spread out')]

    servers_beta_comments = get_comments(toml_source=servers_fixed_order_table, hierarchy='beta')
    assert servers_beta_comments == [(3, '# This nesting is awkward')]

    servers_beta_comments = get_comments(toml_source=servers_fixed_order_table, hierarchy='alpha.metadata')
    assert servers_beta_comments == [(4, '# Too far from papa')]

    # Fix the out-order-table from the TOML document in place
    toml_document_original = copy.deepcopy(toml_document)
    fix_out_of_order_tables(toml_source=toml_document)

    assert toml_document_original == toml_document
    assert not _detect_any_out_of_order_tables(toml_source=toml_document)