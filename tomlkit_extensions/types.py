from __future__ import annotations
from dataclasses import dataclass
from typing import (
    Any,
    List,
    Optional,
    Tuple,
    Union
)

from tomlkit import items

@dataclass(frozen=True)
class Attribute:
    """"""
    index: int
    value: Union[items.Item, items.Table]


class Hierarchy:
    """"""
    def __init__(self, hierarchy: Tuple[str, ...], attribute: str):
        self.hierarchy = hierarchy
        self.attribute = attribute

    def __eq__(self, hierarchy: Any) -> bool:
        if not isinstance(hierarchy, Hierarchy):
            message_core = 'Expected an instance of Hierarchy'
            raise TypeError(f"{message_core}, but got {type(hierarchy).__name__}")
        
        return (
            self.hierarchy == hierarchy.hierarchy and
            self.attribute == hierarchy.attribute
        )
    
    def __str__(self) -> str:
        """"""
        return repr(self)

    def __repr__(self) -> str:
        """"""
        return f'<Hierarchy {self.full_hierarchy_str}>'

    @staticmethod
    def remove_recent_table(hierarchy: str) -> str:
        """"""
        return '.'.join(hierarchy.split('.')[:-1])

    @staticmethod
    def create_hierarchy(hierarchy: str, update: str) -> str:
        """"""
        full_hierarchy = str()

        if hierarchy:
            full_hierarchy += hierarchy
        
        if update and not full_hierarchy:
            full_hierarchy += update
        elif update:
            full_hierarchy += '.' + update

        return full_hierarchy
    
    @classmethod
    def from_str_hierarchy(cls, hierarchy: str) -> Hierarchy:
        """"""
        hirarchy_decomposed = hierarchy.split('.')
        assert len(hirarchy_decomposed) > 0

        return cls.from_list_hierarchy(hierarchy=hirarchy_decomposed)
    
    @classmethod
    def from_list_hierarchy(cls, hierarchy: List[str]) -> Hierarchy:
        """"""
        if not hierarchy:
            raise ValueError("There must be an existing hierarchy")

        if len(hierarchy) == 1:
            attribute = hierarchy[0]
            attribute_hierarchy = list()
        else:
            attribute = hierarchy[-1]
            attribute_hierarchy = hierarchy[:-1]

        return cls(
            attribute=attribute, hierarchy=tuple(attribute_hierarchy)
        )

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
    
    def update_hierarchy(self, update: str) -> None:
        """"""
        update_decomposed: List[str] = update.split('.')
        
        attribute = update_decomposed[-1]
        hierarchy_new = list(self.full_hierarchy)
        if len(update_decomposed) > 1:
            hierarchy_new += update_decomposed[:-1]

        self.hierarchy = tuple(hierarchy_new)
        self.attribute = attribute