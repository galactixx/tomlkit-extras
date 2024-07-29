from typing import (
    cast,
    Iterator,
    Optional,
    overload,
    Union
)

import tomlkit
from tomlkit import (
    items, 
    TOMLDocument
)

from tomlkit_extensions.types import (
    Attribute,
    FieldHierarchy,
    Hierarchy
)

@overload
def get_from_toml(hierarchy: FieldHierarchy, source: TOMLDocument) -> Optional[items.Item]:
    ...


@overload
def get_from_toml(hierarchy: Hierarchy, source: TOMLDocument) -> Optional[items.Table]:
    ...


def get_item_from_toml(
    hierarchy: Union[FieldHierarchy, Hierarchy], source: TOMLDocument
) -> Optional[Union[items.Item, items.Table]]:
    """"""
    current_source: Union[items.Table, TOMLDocument] = source
    for table in hierarchy.hierarchy:
        current_source = cast(items.Table, current_source[table])

    if hierarchy.attribute not in current_source:
        return None
    else:
        return cast(
            Union[items.Item, items.Table], current_source[hierarchy.attribute]
        )
    

def get_attribute_from_toml(
    hierarchy: Union[FieldHierarchy, Hierarchy], source: TOMLDocument
) -> Attribute:
    """"""
    current_source: Union[items.Table, TOMLDocument] = source
    for table in hierarchy.hierarchy:
        current_source = cast(items.Table, current_source[table])
        
    attribute_index = list(current_source.keys()).index(hierarchy.attribute)
    value = cast(
        Union[items.Item, items.Table], current_source[hierarchy.attribute]
    )

    return Attribute(index=attribute_index, value=value)


def create_new_toml(hierarchy: Hierarchy, update: items.Table) -> TOMLDocument:
    """"""
    source: TOMLDocument = tomlkit.document()

    current_source: Union[items.Table, TOMLDocument] = source
    for table in hierarchy.hierarchy:
        current_source[table] = tomlkit.table()
        current_source = cast(items.Table, current_source[table])

    current_source[hierarchy.attribute] = update

    return source


def delete_from_toml(
    source: TOMLDocument, hierarchy: Union[FieldHierarchy, Hierarchy]
) -> None:
    """"""
    def delete(
        current_source: Union[TOMLDocument, items.Table],
        hierarchy_iter: Iterator[str]
    ) -> None:
        """"""
        try:
            current_table = next(hierarchy_iter)
        except StopIteration:
            del current_source[hierarchy.attribute]
        else:
            next_source = cast(items.Table, current_source[current_table])
            delete(
                current_source=next_source,
                hierarchy_iter=hierarchy_iter
            )

            if not current_source[current_table]:
                del current_source[current_table]

    hierarchy_iter: Iterator[str] = iter(hierarchy.hierarchy)
    delete(current_source=source, hierarchy_iter=hierarchy_iter)


def update_table_in_toml(
    source: TOMLDocument, hierarchy: Hierarchy, update: items.Table
) -> TOMLDocument:
    """"""
    def update_toml(source: Union[items.Table, TOMLDocument], update: items.Table) -> None:
        """"""
        for key, value in update.items():
            if isinstance(value, items.Table):
                if key not in source:
                    source[key] = tomlkit.table()

                next_source = cast(items.Table, source[key])
                update_toml(source=next_source, update=value)
            else:
                source.update({key: value})

    current_source: Union[items.Table, TOMLDocument] = source
    for table in hierarchy.full_hierarchy:
        current_source = cast(items.Table, current_source[table])

    update_toml(source=current_source, update=update)

    return source


def add_to_toml(
    source: TOMLDocument,
    hierarchy: Union[FieldHierarchy, Hierarchy],
    update: Union[items.Table, items.Item],
    index: Optional[int] = None
) -> None:
    """"""
    current_source: Union[items.Table, TOMLDocument] = source
    for table in hierarchy.hierarchy:
        if table not in current_source:
            current_source[table] = dict()

        parent_local: Union[items.Table, TOMLDocument] = current_source
        current_source = cast(items.Table, current_source[table])
        
    if index is not None:
        source_as_list = list(current_source.items())
        source_as_list.insert(index, (hierarchy.attribute, update))

        updated_object: Union[items.Table, TOMLDocument]

        if isinstance(current_source, TOMLDocument):
            updated_object = tomlkit.document()

            updated_object.update(dict(source_as_list))
            source = updated_object

        # Else it is a items.Table instance
        else:
            updated_object = tomlkit.table()

            # Copy over comment from original table instance
            updated_object.comment(comment=current_source.trivia.comment)
            updated_object.update(dict(source_as_list))

            parent_local[table] = updated_object
    else:
        current_source[hierarchy.attribute] = update