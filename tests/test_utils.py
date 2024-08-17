from typing import (
    Any,
    Dict,
    List,
    Tuple
)

import tomlkit
from tomlkit.container import OutOfOrderTableProxy
from tomlkit import items, TOMLDocument
from tomlkit_extras import (
    get_attribute_from_toml_source,
    load_toml_file
)

from tomlkit_extras._typing import ContainerBodyItem
from tomlkit_extras._utils import (
    complete_clear_toml_document,
    create_array_of_tables,
    create_toml_document,
    decompose_body_item,
    from_dict_to_toml_document,
    get_container_body,
    partial_clear_dict_like_toml_item
)

def _number_of_top_level_attributes(toml_document: TOMLDocument) -> int:
    """"""
    num_attributes = 0
    for _, _ in toml_document.items():
        num_attributes += 1

    return num_attributes


def _document_partial_clear_assertion(num_attributes: int, toml_document: TOMLDocument) -> None:
    """"""
    assert _number_of_top_level_attributes(toml_document=toml_document) == num_attributes
    partial_clear_dict_like_toml_item(toml_source=toml_document)
    assert _number_of_top_level_attributes(toml_document=toml_document) == 0


def _document_complete_clear_assertion(num_attributes: int, toml_document: TOMLDocument) -> None:
    """"""
    assert _number_of_top_level_attributes(toml_document=toml_document) == num_attributes
    complete_clear_toml_document(toml_document=toml_document)
    assert _number_of_top_level_attributes(toml_document=toml_document) == 0

    assert toml_document._map == {}
    assert toml_document._body == []
    assert toml_document._parsed == False
    assert toml_document._table_keys == []


def _validate_body_items(container_body: List[Tuple[Any, Any]]) -> bool:
    """"""
    return all(
        (item_key is None or isinstance(item_key, items.Key)) and isinstance(item, items.Item)
        for (item_key, item) in container_body
    )


def _validate_body_item(body_item: ContainerBodyItem) -> bool:
    """"""
    item_key, toml_item = decompose_body_item(body_item=body_item)
    return (item_key is None or isinstance(item_key, str)) and isinstance(toml_item, items.Item)


def _table_from_dict(to_table: Dict[str, Any]) -> items.Table:
    """"""
    table: items.Table = tomlkit.table()
    table.update(to_table)
    return table


def test_convert_to_tomlkit_item() -> None:
    """"""
    pass


def test_complete_clear_toml_document() -> None:
    """"""
    toml_document_b: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_b.toml')
    _document_complete_clear_assertion(num_attributes=3, toml_document=toml_document_b)

    toml_document_d: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_d.toml')
    _document_complete_clear_assertion(num_attributes=4, toml_document=toml_document_d)


def test_create_array_of_tables() -> None:
    """"""
    RAW_TABLE_DICTS = [{'name': 'Sub Table 1', 'value': 10}, {'name': 'Sub Table 2', 'value': 20}]

    # Create an array of tables from a list of dictionaries
    aot_from_dictionaries = create_array_of_tables(tables=RAW_TABLE_DICTS)
    assert isinstance(aot_from_dictionaries, items.AoT)
    assert len(aot_from_dictionaries) == 2

    # Create an array of tables from a list of Table instances
    raw_table_dicts_to_tables = [_table_from_dict(to_table=table) for table in RAW_TABLE_DICTS]
    aot_from_table_instances = create_array_of_tables(tables=raw_table_dicts_to_tables)
    assert isinstance(aot_from_table_instances, items.AoT)
    assert len(aot_from_table_instances) == 2

    # Create an array of tables from a list of dictionaries and Table instances
    aot_from_combined = create_array_of_tables(tables=[
        raw_table_dicts_to_tables[0], RAW_TABLE_DICTS[1]
    ])
    assert isinstance(aot_from_combined, items.AoT)
    assert len(aot_from_combined) == 2    


def test_create_toml_document() -> None:
    """"""
    toml_document: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_a.toml')

    # Retrieve a couple items from the document to serve as inputs
    # to the create_toml_document function

    # Test on the project table
    project = get_attribute_from_toml_source(hierarchy='project', toml_source=toml_document)
    assert isinstance(project, items.Table)

    project_toml_document = create_toml_document(hierarchy='project.update', update=project)
    assert isinstance(project_toml_document, TOMLDocument)
    assert project_toml_document.unwrap() == {'project': {'update': {'name': 'Example Project'}}}

    # Test on the details table
    details = get_attribute_from_toml_source(hierarchy='details', toml_source=toml_document)
    assert isinstance(details, items.Table)

    details_toml_document = create_toml_document(hierarchy='details.new.update', update=details)
    assert isinstance(details_toml_document, TOMLDocument)
    assert details_toml_document.unwrap() == {
        'details': {'new': {'update': {'description': 'A sample project configuration'}}}
    }

    # Test on the members array of tables
    members = get_attribute_from_toml_source(hierarchy='members.roles', toml_source=toml_document)
    assert isinstance(members, list)
    assert isinstance(members[0], items.AoT)

    members_toml_document = create_toml_document(hierarchy='members.roles.update', update=members[0])
    assert isinstance(members_toml_document, TOMLDocument)
    assert members_toml_document.unwrap() == {
        "members": {'roles': {'update': [{'role': 'Developer'}, {'role': 'Designer'}]}}
    }


def test_decompose_body_item() -> None:
    """"""
    toml_document_a: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_a.toml')
    document_body = get_container_body(toml_source=toml_document_a)
    assert all(
        _validate_body_item(body_item=body_item) for body_item in document_body
    )

    # Test the function on the body of the tool.ruff.lint table
    toml_document_b: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_b.toml')
    tool_ruff_lint = get_attribute_from_toml_source(hierarchy='tool.ruff.lint', toml_source=toml_document_b)
    assert isinstance(tool_ruff_lint, items.Table)
    table_body = get_container_body(toml_source=tool_ruff_lint)
    assert all(
        _validate_body_item(body_item=body_item) for body_item in table_body
    )


def test_from_dict_to_toml_document() -> None:
    """"""
    # The below assertions are just ensuring that the structure and values
    # of the converted dictionary are the same. Of course this convereted dictionary
    # is missing comments and the inline table in this case will be converted to a table.
    toml_document_c: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_c.toml')
    DICT_CONVERT_C = {
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
    toml_convert_document_c =  from_dict_to_toml_document(dictionary=DICT_CONVERT_C)
    assert isinstance(toml_convert_document_c, TOMLDocument)
    assert toml_convert_document_c == toml_document_c

    toml_document_b: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_b.toml')
    DICT_CONVERT_B = {
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
    }
    toml_convert_document_b = from_dict_to_toml_document(dictionary=DICT_CONVERT_B)
    assert isinstance(toml_convert_document_b, TOMLDocument)
    assert toml_convert_document_b == toml_document_b


def test_get_container_body() -> None:
    """"""
    toml_document_b: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_b.toml')

    # Retrieve the container from a TOMLDocument instance
    document_container = get_container_body(toml_source=toml_document_b)
    assert isinstance(toml_document_b, TOMLDocument)
    assert _validate_body_items(container_body=document_container)

    # Retrieve the container from a Table instance
    table_ruff = get_attribute_from_toml_source(hierarchy='tool.ruff', toml_source=toml_document_b)
    assert isinstance(table_ruff, items.Table)
    table_container = get_container_body(toml_source=table_ruff)
    assert _validate_body_items(container_body=table_container)

    # Retrieve the container from a InlineTable instance
    table_pydocstyle = get_attribute_from_toml_source(
        hierarchy='tool.ruff.lint.pydocstyle', toml_source=toml_document_b
    )
    assert isinstance(table_pydocstyle, items.InlineTable)
    inline_table_container = get_container_body(toml_source=table_pydocstyle)
    assert _validate_body_items(container_body=inline_table_container)

    toml_document_c: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_c.toml')

    # Retrieve the container from an Array instance
    array_dev_dependencies = get_attribute_from_toml_source(
        hierarchy='tool.rye.dev-dependencies', toml_source=toml_document_c
    )
    assert isinstance(array_dev_dependencies, items.Array)
    array_container = get_container_body(toml_source=array_dev_dependencies)
    assert _validate_body_items(container_body=array_container)

    # Retrieve the container from an OutOfOrderTableProxy instance
    out_of_order_proxy_ruff = get_attribute_from_toml_source(
        hierarchy='tool.ruff', toml_source=toml_document_c
    )
    assert isinstance(out_of_order_proxy_ruff, OutOfOrderTableProxy)
    out_of_order_proxy_container = get_container_body(toml_source=out_of_order_proxy_ruff)
    assert _validate_body_items(container_body=out_of_order_proxy_container)


def test_partial_clear_dict_like_toml_item() -> None:
    """"""
    toml_document_a: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_a.toml')
    _document_partial_clear_assertion(num_attributes=3, toml_document=toml_document_a)

    toml_document_b: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_b.toml')
    _document_partial_clear_assertion(num_attributes=3, toml_document=toml_document_b)

    toml_document_d: TOMLDocument = load_toml_file(toml_source=r'tests\examples\toml_d.toml')
    _document_partial_clear_assertion(num_attributes=4, toml_document=toml_document_d)