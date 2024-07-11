from __future__ import annotations
from abc import ABC, abstractmethod
from typing import (
    Any,
    List,
    Tuple,
    Type,
    TypeVar
)

_Hierarchy = TypeVar('_Hierarchy', bound='BaseHierarchy')

class BaseHierarchy(ABC):
    """"""
    def __init__(self, hierarchy: Tuple[str, ...], attribute: str):
        self.hierarchy = hierarchy
        self.attribute = attribute

    def __eq__(self, hierarchy: Any) -> bool:
        if not isinstance(hierarchy, BaseHierarchy):
            raise TypeError(
                f"Expected an instance of BaseHierarchy, but got {type(hierarchy).__name__}"
            )
        
        return (
            self.hierarchy == hierarchy.hierarchy and
            self.attribute == hierarchy.attribute
        )
    
    @classmethod
    @abstractmethod
    def from_str_hierarchy(cls: Type[_Hierarchy], hierarchy: str) -> _Hierarchy:
        """"""
        pass

    @staticmethod
    def consolidate_hierarchy(hierarchy: List[str]) -> str:
        """"""
        return '.'.join(hierarchy)

    @property
    def full_hierarchy(self) -> Tuple[str, ...]:
        """"""
        return tuple(list(self.hierarchy) + [self.attribute])
    
    @property
    def base_hierarchy_str(self) -> str:
        """"""
        return '.'.join(self.hierarchy)
    
    @property
    def full_hierarchy_str(self) -> str:
        """"""
        if not self.base_hierarchy_str:
            return self.attribute
        else:
            return '.'.join(self.full_hierarchy)


class FieldHierarchy(BaseHierarchy):
    """"""
    def __init__(
        self, field: str, hierarchy: Tuple[str, ...] = tuple()
    ):
        super().__init__(hierarchy=hierarchy, attribute=field)

    @classmethod
    def from_str_hierarchy(cls, hierarchy: str) -> FieldHierarchy:
        """"""
        hirarchy_decomposed = hierarchy.split('.')
        assert len(hirarchy_decomposed) > 1

        return cls(
            field=hirarchy_decomposed[-1],
            hierarchy=tuple(hirarchy_decomposed[:-1])
        )


class Hierarchy(BaseHierarchy):
    """"""
    def __init__(
        self, table: str, hierarchy: Tuple[str, ...] = tuple()
    ):
        super().__init__(hierarchy=hierarchy, attribute=table)
    
    @classmethod
    def from_str_hierarchy(cls, hierarchy: str) -> Hierarchy:
        """"""
        return cls.from_list_hierarchy(hierarchy=hierarchy.split('.'))

    @classmethod
    def from_list_hierarchy(cls, hierarchy: List[str]) -> Hierarchy:
        """"""
        if not hierarchy:
            raise ValueError("There must be an existing hierarchy")

        if len(hierarchy) == 1:
            table = hierarchy[0]
            table_hierarchy = list()
        else:
            table = hierarchy[-1]
            table_hierarchy = hierarchy[:-1]

        return cls(
            table=table, hierarchy=tuple(table_hierarchy)
        )