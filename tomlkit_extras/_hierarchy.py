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

def standardize_hierarchy(hierarchy: 'TOMLHierarchy') -> Hierarchy:
    """
    Accepts a `TOMLHierarchy` instance, being an instance of string or `Hierarchy`,
    and returns a `Hierarchy` instance.

    Args:
        hierarchy (`TOMLHierarchy`) A `TOMLHierarchy` instance.

    Returns:
        `Hierarchy`: A `Hierarchy` instance.
    """
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
            message_core = 'Expected an instance of string or Hierarchy'
            return TypeError(f"{message_core}, but got {type(hierarchy).__name__}")

        hierarchy_arg = standardize_hierarchy(hierarchy=hierarchy)
        return (
            self.hierarchy == hierarchy_arg.hierarchy and
            self.attribute == hierarchy_arg.attribute
        )
    
    def __str__(self) -> str:
        return self.full_hierarchy_str

    def __repr__(self) -> str:
        return f'<Hierarchy {self.full_hierarchy_str}>'
    
    def __len__(self) -> int:
        return self.hierarchy_depth
    
    @staticmethod
    def parent_level(hierarchy: str) -> str:
        """

        """
        return hierarchy.split('.')[-1]

    @staticmethod
    def parent_hierarchy(hierarchy: str) -> str:
        """
        A static method which returns the parent hierarchy of a string
        representation of a TOML hierarchy.

        Args:
            hierarchy (str): A string representation of a TOML hierarchy.

        Returns:
            str: A string instance representing the parent TOML hierarchy of the
                hierarchy passed in.
        """
        return '.'.join(hierarchy.split('.')[:-1])

    @staticmethod
    def create_hierarchy(hierarchy: str, attribute: str) -> str:
        """
        A static method which creates a string representation of a TOML hierarchy
        from a string TOML hierarchy and an update string instance.

        Args:
            hierarchy (str) A string instance representing a TOML hierarchy.
            attribute (str): An attribute to be added to the existing hierarchy.

        Returns:
            str: A string instance representing an updated TOML hierarchy.
        """
        full_hierarchy = str()

        if hierarchy:
            full_hierarchy += hierarchy
        
        if attribute and not full_hierarchy:
            full_hierarchy += attribute
        elif attribute:
            full_hierarchy += '.' + attribute

        return full_hierarchy
    
    @classmethod
    def from_str_hierarchy(cls, hierarchy: str) -> Hierarchy:
        """
        A class method which returns a `Hierarchy` instance from a string instance of
        a TOML hierarchy.
        
        Args:
            hierarchy (str) A string instance representing a TOML hierarchy.

        Returns:
            `Hierarchy`: A `Hierarchy` instance.
        """
        hirarchy_decomposed = hierarchy.split('.')
        assert len(hirarchy_decomposed) > 0

        return cls.from_list_hierarchy(hierarchy=hirarchy_decomposed)
    
    @classmethod
    def from_list_hierarchy(cls, hierarchy: List[str]) -> Hierarchy:
        """
        A class method which returns a `Hierarchy` instance from a list instance of
        strings representing each individual level in a TOML hierarchy.
        
        Args:
            hierarchy (List[str]) A list instance of strings representing each
                individual level in a TOML hierarchy

        Returns:
            `Hierarchy`: A `Hierarchy` instance.
        """
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
        """
        Returns the depth of the hierarchy, also known as the number of levels
        in the hierarchy.
        """
        return len(self.full_hierarchy)

    @property
    def root_attribute(self) -> str:
        """Returns the root/first level of the hierarchy."""
        if not self.hierarchy:
            return self.attribute
        else:
            return self.hierarchy[0]

    @property
    def full_hierarchy(self) -> Tuple[str, ...]:
        """Returns a tuple instance of the entire hierarchy."""
        return tuple(list(self.hierarchy) + [self.attribute])
    
    @property
    def base_hierarchy_str(self) -> str:
        """
        Returns a string instance of the entire hierarchy minus the attribute/last
        level.
        """
        return '.'.join(self.hierarchy)
    
    @property
    def full_hierarchy_str(self) -> str:
        """Returns a string instance of the entire hierarchy."""
        if not self.base_hierarchy_str:
            return self.attribute
        else:
            return '.'.join(self.full_hierarchy)
        
    @property
    def ancestor_hierarchies(self) -> List[str]:
        """
        Returns a list of strings representing all ancestor hierarchies of the current
        hierarchy.
        """
        sub_hierarchies: List[str] = []

        start_hierarchy = str()
        for hierarchy in self.full_hierarchy:
            start_hierarchy = Hierarchy.create_hierarchy(hierarchy=start_hierarchy, attribute=hierarchy)
            sub_hierarchies.append(start_hierarchy)

        return sub_hierarchies
        
    def shortest_ancestor_hierarchy(self, hierarchies: Set[str]) -> Optional[str]:
        """
        Returns the shortest hierarchy appearing in a set of string instances being
        an ancestor of the current hierarchy.

        Will return None if no hierarchy found in the set is an ancestor of the
        current hierarchy.
        
        Args:
            hierarchies (Set[str]): A set of strings representing TOML hierarchies.

        Returns:
            str | None: A string instance or None.
        """
        ancestor_hierarchies = sorted(self.ancestor_hierarchies, key=lambda x: len(x))
        return self._ancestor_hierarchy_match(
            ancestor_hierarchies=ancestor_hierarchies, hierarchies=hierarchies
        )
    
    def longest_ancestor_hierarchy(self, hierarchies: Set[str]) -> Optional[str]:
        """
        Returns the longest hierarchy appearing in a set of string instances being
        an ancestor of the current hierarchy.
        
        Will return None if no hierarchy found in the set is an ancestor of the
        current hierarchy.

        Args:
            hierarchies (Set[str]): A set of strings representing TOML hierarchies.

        Returns:
            str | None: A string instance or None.
        """
        ancestor_hierarchies = sorted(self.ancestor_hierarchies, key=lambda x: -len(x))
        return self._ancestor_hierarchy_match(
            ancestor_hierarchies=ancestor_hierarchies, hierarchies=hierarchies
        )

    def _ancestor_hierarchy_match(self, ancestor_hierarchies: List[str], hierarchies: Set[str]) -> Optional[str]:
        """
        A private method that returns the first ancestor hierarchy appearing in a
        set of other string hierarchies.

        Will return None if no ancestor hierarchy was found.
        """
        for hierarchy in ancestor_hierarchies:
            if hierarchy in hierarchies:
                return hierarchy
            
        return None
    
    def add_to_hierarchy(self, update: str) -> None:
        """
        Appends at least one more level to the existing hierarchy, which updates both
        the hierarchy and attribute data fields.

        Args:
            update (str): A string instance to append to the existing hierarchy.
        """
        update_decomposed: List[str] = update.split('.')
        
        attribute = update_decomposed[-1]
        hierarchy_new = list(self.full_hierarchy)
        if len(update_decomposed) > 1:
            hierarchy_new += update_decomposed[:-1]

        self.hierarchy = tuple(hierarchy_new)
        self.attribute = attribute

    def is_child_hierarchy(self, hierarchy: str) -> bool:
        """
        Returns a boolean indicating whether the hierarchy passed in as an argument
        is a child of the current hierarchy.
        
        Args:
            hierarchy (str): A string representation of a TOML hierarchy.

        Returns:
            bool: A boolean indicating whether it is a child hierarchy of the current
                hierarchy.
        """
        parent_hierarchy = Hierarchy.parent_hierarchy(hierarchy=hierarchy)
        return self == parent_hierarchy