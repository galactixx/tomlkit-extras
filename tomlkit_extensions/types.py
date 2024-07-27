from __future__ import annotations
from abc import ABC, abstractmethod
from typing import (
    Any,
    List,
    Optional,
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
            message_core = 'Expected an instance of BaseHierarchy'
            raise TypeError(f"{message_core}, but got {type(hierarchy).__name__}")
        
        return self.hierarchy == hierarchy.hierarchy and self.attribute == hierarchy.attribute
    
    @abstractmethod
    def __str__(self) -> str:
        """"""
        pass

    @abstractmethod
    def __repr__(self) -> str:
        """"""
        pass

    @classmethod
    @abstractmethod
    def from_str_hierarchy(cls: Type[_Hierarchy], hierarchy: str) -> _Hierarchy:
        """"""
        pass

    @staticmethod
    def remove_recent_table(hierarchy: str) -> str:
        """"""
        return '.'.join(hierarchy.split('.')[:-1])

    @staticmethod
    def update_hierarchy(hierarchy: str, update: str) -> str:
        """"""
        return hierarchy + '.' + update if hierarchy else update
    
    @property
    def hierarchy_depth(self) -> int:
        """"""
        return len(self.full_hierarchy)

    @property
    def root_attribute(self) -> str:
        """"""
        if not self.hierarchy:
            return self.attribute
        else:
            return self.hierarchy[0]

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
        
    def shortest_sub_hierarchy(self, hierarchies: List[str]) -> Optional[str]:
        """"""
        hierarchies_sorted = sorted(hierarchies, key=lambda x: len(x))
        return self._sub_hierarchy_match(hierarchies=hierarchies_sorted)
    
    def longest_sub_hierarchy(self, hierarchies: List[str]) -> Optional[str]:
        """"""
        hierarchies_sorted = sorted(hierarchies, key=lambda x: -len(x))
        return self._sub_hierarchy_match(hierarchies=hierarchies_sorted)
        
    def _sub_hierarchy_match(self, hierarchies: List[str]) -> Optional[str]:
        """"""
        for hierarchy in hierarchies:
            if self.full_hierarchy_str.startswith(hierarchy):
                return hierarchy
            
        return None
    

class FieldHierarchy(BaseHierarchy):
    """"""
    def __init__(
        self, field: str, hierarchy: Tuple[str, ...] = tuple()
    ):
        super().__init__(hierarchy=hierarchy, attribute=field)

    def __str__(self) -> str:
        """"""
        return repr(self)

    def __repr__(self) -> str:
        """"""
        return f'<FieldHierarchy {self.full_hierarchy_str}>' 

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
    
    def __str__(self) -> str:
        """"""
        return repr(self)

    def __repr__(self) -> str:
        """"""
        return f'<Hierarchy {self.full_hierarchy_str}>'

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