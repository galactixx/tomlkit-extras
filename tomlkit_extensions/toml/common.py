from typing import (
    Optional,
    Tuple
)

from tomlkit import TOMLDocument

from tomlkit_extensions.typing import TOMLRetrieval
from tomlkit_extensions.hierarchy import Hierarchy
from tomlkit_extensions.toml.retrieval import get_attribute_from_toml_source

def _find_parent_source(hierarchy: Hierarchy, toml_source: TOMLDocument) -> TOMLRetrieval:
    """"""
    hierarchy_parent = Hierarchy.parent_hierarchy(hierarchy=str(hierarchy))
    return get_attribute_from_toml_source(
        hierarchy=hierarchy_parent, toml_source=toml_source
    )


def find_parent_toml_source(hierarchy: Hierarchy, toml_source: TOMLDocument) -> TOMLRetrieval:
    """"""
    if hierarchy.hierarchy_depth > 1:
        parent_toml = _find_parent_source(hierarchy=hierarchy, toml_source=toml_source)
    else:
        parent_toml = toml_source

    return parent_toml


def find_parent_toml_sources(hierarchy: Hierarchy, toml_source: TOMLDocument) -> Tuple[
    Optional[TOMLRetrieval], TOMLRetrieval
]:
    """"""
    if hierarchy.hierarchy_depth > 1:
        parent_toml = _find_parent_source(hierarchy=hierarchy, toml_source=toml_source)

        if hierarchy.hierarchy_depth > 2:
            grandparent_toml = _find_parent_source(
                hierarchy=Hierarchy.parent_hierarchy(hierarchy=str(hierarchy)),
                toml_source=toml_source
            )
        else:
            grandparent_toml = toml_source
    else:
        grandparent_toml = None
        parent_toml = toml_source

    return grandparent_toml, parent_toml