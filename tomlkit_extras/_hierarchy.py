from __future__ import annotations
from typing import (
    Any,
    List,
    Optional,
    Set,
    Tuple,
    TYPE_CHECKING
)

if TYPE_CHECKING:
    from tomlkit_extras._typing import TOMLHierarchy

def _hierarchy_type_error(hierarchy: Any) -> TypeError:
    """"""
    message_core = 'Expected an instance of string or Hierarchy'
    return TypeError(f"{message_core}, but got {type(hierarchy).__name__}")


def standardize_hierarchy(hierarchy: 'TOMLHierarchy') -> Hierarchy:
    """"""
    if isinstance(hierarchy, str):
        hierarchy_final = Hierarchy.from_str_hierarchy(hierarchy=hierarchy)
    else:
        hierarchy_final = hierarchy
    return hierarchy_final


class Hierarchy:
    """"""
    def __init__(self, hierarchy: Tuple[str, ...], attribute: str):
        self.hierarchy = hierarchy
        self.attribute = attribute

    def __eq__(self, hierarchy: Any) -> bool:
        if not isinstance(hierarchy, (str, Hierarchy)):
            raise _hierarchy_type_error(hierarchy=hierarchy)

        hierarchy_arg = standardize_hierarchy(hierarchy=hierarchy)
        return (
            self.hierarchy == hierarchy_arg.hierarchy and
            self.attribute == hierarchy_arg.attribute
        )
    
    def __str__(self) -> str:
        """"""
        return self.full_hierarchy_str

    def __repr__(self) -> str:
        """"""
        return f'<Hierarchy {self.full_hierarchy_str}>'
    
    def __len__(self) -> int:
        """"""
        return self.hierarchy_depth

    @staticmethod
    def parent_hierarchy(hierarchy: str) -> str:
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
        
    @property
    def sub_hierarchies(self) -> List[str]:
        """"""
        sub_hierarchies: List[str] = []

        start_hierarchy = str()
        for hierarchy in self.full_hierarchy:
            start_hierarchy = Hierarchy.create_hierarchy(hierarchy=start_hierarchy, update=hierarchy)
            sub_hierarchies.append(start_hierarchy)

        return sub_hierarchies

    def diff(self, hierarchy: Any) -> Optional[Hierarchy]:
        """"""
        if not isinstance(hierarchy, (str, Hierarchy)):
            raise _hierarchy_type_error(hierarchy=hierarchy)
        
        hierarchy_obj = standardize_hierarchy(hierarchy=hierarchy)

        if hierarchy_obj == self:
            return None

        if not self.full_hierarchy_str.startswith(hierarchy_obj.full_hierarchy_str):
            raise ValueError(
                "Hierarchy argument must be a sub-hierarchy of the Hierarchy instance"
            )
        
        remaining_heirarchy = self.full_hierarchy_str.replace(
            hierarchy_obj.full_hierarchy_str, str()
        )
        remaining_heirarchy = remaining_heirarchy.lstrip('.')

        return Hierarchy.from_str_hierarchy(hierarchy=remaining_heirarchy)
        
    def shortest_sub_hierarchy(self, hierarchies: Set[str]) -> Optional[str]:
        """"""
        sub_hierarchies = sorted(self.sub_hierarchies, key=lambda x: len(x))
        return self._sub_hierarchy_match(
            sub_hierarchies=sub_hierarchies, hierarchies=hierarchies
        )
    
    def longest_sub_hierarchy(self, hierarchies: Set[str]) -> Optional[str]:
        """"""
        sub_hierarchies = sorted(self.sub_hierarchies, key=lambda x: -len(x))
        return self._sub_hierarchy_match(
            sub_hierarchies=sub_hierarchies, hierarchies=hierarchies
        )

    def _sub_hierarchy_match(self, sub_hierarchies: List[str], hierarchies: Set[str]) -> Optional[str]:
        """"""
        for hierarchy in sub_hierarchies:
            if hierarchy in hierarchies:
                return hierarchy
            
        return None
    
    def add_to_hierarchy(self, update: str) -> None:
        """"""
        update_decomposed: List[str] = update.split('.')
        
        attribute = update_decomposed[-1]
        hierarchy_new = list(self.full_hierarchy)
        if len(update_decomposed) > 1:
            hierarchy_new += update_decomposed[:-1]

        self.hierarchy = tuple(hierarchy_new)
        self.attribute = attribute

    def is_child_hierarchy(self, hierarchy: str) -> bool:
        """"""
        parent_hierarchy = Hierarchy.parent_hierarchy(hierarchy=hierarchy)
        return self == parent_hierarchy