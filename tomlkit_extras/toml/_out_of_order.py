import copy
from typing import (
    Any,
    cast,
    Iterator,
    List,
    Optional
)

from tomlkit import items, TOMLDocument
from tomlkit.container import OutOfOrderTableProxy

from tomlkit_extras._typing import TOMLSource

def _fix_of_out_of_order_table_chain(
    current_table: items.Table, update_key: str, update_table: items.Table
) -> items.Table:
    """"""
    if update_key not in current_table:
        current_table[update_key] = update_table
    else:
        update_from_table: items.Table = _find_child_table(table_value=current_table[update_key])

        if update_from_table.is_super_table():
            new_current_table = update_table
            new_update_table = update_from_table
            current_table[update_key] = update_table
        else:
            new_current_table = update_from_table
            new_update_table = update_table

        for table_key, table_value in new_update_table.items():
            child_table = _find_child_table(table_value=table_value)

            _fix_of_out_of_order_table_chain(
                current_table=new_current_table, update_key=table_key, update_table=child_table
            )


def _find_child_table(table_value: Any) -> items.Table:
    """"""
    if isinstance(table_value, OutOfOrderTableProxy):
        child_table = fix_out_of_order_table(table=table_value)
    else:
        child_table = table_value
    return child_table


def fix_out_of_order_table(table: OutOfOrderTableProxy) -> items.Table:
    """"""
    component_tables = cast(List[items.Table], copy.deepcopy(table._tables))

    table_w_shortest_name: Optional[items.Table] = None
    parent_table: Optional[items.Table] = None

    component_tables_iter: Iterator[items.Table] = iter(component_tables)

    try:
        while parent_table is None:
            co_table: items.Table = next(component_tables_iter)

            if not co_table.is_super_table():
                parent_table = co_table
            elif co_table.name is not None and table_w_shortest_name is None:
                table_w_shortest_name = co_table
            elif (
                co_table.name is not None and
                len(co_table.name) < len(table_w_shortest_name.name)
            ):
                table_w_shortest_name = co_table
    except StopIteration:
        parent_table = table_w_shortest_name

    component_tables.remove(parent_table)

    for component_table in component_tables:
        current_table = parent_table

        for table_key, table_value in component_table.items():
            child_table: items.Table = _find_child_table(table_value=table_value)

            _fix_of_out_of_order_table_chain(
                current_table=current_table, update_key=table_key, update_table=child_table
            )

    return parent_table


def fix_out_of_order_tables(toml_source: TOMLSource) -> None:
    """"""
    if isinstance(toml_source, (items.Table, TOMLDocument)):
        for table_key, table_value in toml_source.items():
            if isinstance(table_value, OutOfOrderTableProxy):
                toml_source[table_key] = fix_out_of_order_table(table=table_value)
            elif isinstance(table_value, items.Table):
                fix_out_of_order_tables(toml_source=table_value)
    elif isinstance(toml_source, items.AoT):
        for aot_table in toml_source:
            fix_out_of_order_tables(toml_source=aot_table)
    else:
        message_core = 'Expected an instance of TOMLSource'
        raise TypeError(f"{message_core}, but got {type(toml_source).__name__}")