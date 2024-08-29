from abc import ABC, abstractmethod
from typing import (
    Any,
    cast,
    Dict,
    Optional,
    Set
)

from tomlkit import items

from tomlkit_extras.descriptor._helpers import (
    item_is_table,
    LineCounter
)
from tomlkit_extras._hierarchy import Hierarchy
from tomlkit_extras._typing import (
    BodyContainerInOrder,
    Item,
    Stylings,
    Table,
    TOMLHierarchy
)
from tomlkit_extras.descriptor._types import (
    ArrayOfTables,
    ArrayOfTablesPosition,
    FieldPosition,
    ItemPosition,
    StylingPositions,
    TablePosition,
    ItemInfo
)

class BaseStore(ABC):
    """"""
    @abstractmethod
    def get(self, hierarchy: str) -> Any:
        pass

    @abstractmethod
    def contains(self, hierarchy: str) -> bool:
        pass

    @abstractmethod
    def update(self, item: items.Item, info: ItemInfo, position: ItemPosition) -> None:
        pass

    @abstractmethod
    def get_stylings(
        self, container_info: ItemInfo,  style_info: ItemInfo
    ) -> StylingPositions:
        pass

    @abstractmethod
    def get_array(self, info: ItemInfo) -> FieldPosition:
        pass


class BaseTableStore(BaseStore):
    """"""
    @property
    @abstractmethod
    def hierarchies(self) -> Set[str]:
        pass

    @abstractmethod
    def add_table(
        self, 
        hierarchy: str, 
        table: Table, 
        info: ItemInfo,
        position: ItemPosition
    ) -> None:
        pass


class DocumentStore(BaseStore):
    """"""
    def __init__(self) -> None:
        self._document_fields: Dict[str, FieldPosition] = dict()
        self._document_stylings: StylingPositions = StylingPositions(
            comments=dict(), whitespace=dict()
        )

    def get(self, hierarchy: str) -> FieldPosition:
        """"""
        return self._document_fields[hierarchy]
    
    def contains(self, hierarchy: str) -> bool:
        """"""
        return hierarchy in self._document_fields

    def update(self, item: items.Item, info: ItemInfo, position: ItemPosition) -> None:
        """"""
        self._document_fields[info.key] = FieldPosition.from_toml_item(
            item=item, info=info, line_no=LineCounter.line_no, position=position
        )

    def get_stylings(self, container_info: ItemInfo, style_info: ItemInfo) -> StylingPositions:
        """"""
        if container_info.item_type.item_type == 'document':
            styling_positions = self._document_stylings
        else:
            styling_positions = self._document_fields[container_info.key].styling
        return styling_positions
    
    def get_array(self, info: ItemInfo) -> FieldPosition:
        """"""
        return self._document_fields[info.key]


class ArrayOfTablesStore(BaseTableStore):
    """"""
    def __init__(self) -> None:
        self._array_of_tables: Dict[str, ArrayOfTables] = dict()

    @property
    def hierarchies(self) -> Set[str]:
        """"""
        return set(self._array_of_tables.keys())

    def get(self, hierarchy: str) -> ArrayOfTables:
        """"""
        return self._array_of_tables[hierarchy]
    
    def contains(self, hierarchy: str) -> bool:
        """"""
        return hierarchy in self._array_of_tables

    def append(self, hierarchy: str, array_of_tables: ArrayOfTablesPosition) -> None:
        """"""
        if not hierarchy in self._array_of_tables:
            self._array_of_tables[hierarchy] = ArrayOfTables(
                aots=[array_of_tables], array_indices={hierarchy: 0}
            )
        else:
            self._array_of_tables[hierarchy].update_arrays(hierarchy=hierarchy, array=array_of_tables)

    def get_array_hierarchy(self, hierarchy: TOMLHierarchy) -> Optional[str]:
        """"""
        if isinstance(hierarchy, Hierarchy):
            hierarchy_obj = hierarchy
        else:
            hierarchy_obj = Hierarchy.from_str_hierarchy(hierarchy=hierarchy)
        
        return hierarchy_obj.longest_ancestor_hierarchy(
            hierarchies=set(self._array_of_tables.keys())
        )
    
    def get_aot_table(self, hierarchy: str) -> TablePosition:
        """"""
        array_hierarchy = cast(str, self.get_array_hierarchy(hierarchy=hierarchy))
        array_of_tables = self._array_of_tables[array_hierarchy]

        return array_of_tables.get_array(hierarchy=hierarchy).get_table(hierarchy=hierarchy)

    def update(self, item: items.Item, info: ItemInfo, position: ItemPosition) -> None:
        """"""
        array_hierarchy = cast(str, self.get_array_hierarchy(hierarchy=info.hierarchy))
        array_of_tables = self._array_of_tables[array_hierarchy]

        array = array_of_tables.get_array(hierarchy=info.hierarchy)
        table = array.get_table(hierarchy=info.hierarchy)
        table.add_field(item=item, info=info, line_no=LineCounter.line_no, position=position)

    def add_table(
        self,
        hierarchy: str,
        table: Table,
        info: ItemInfo,
        position: ItemPosition
    ) -> None:
        """"""
        array_hierarchy = cast(str, self.get_array_hierarchy(hierarchy=hierarchy))
        array_of_tables = self._array_of_tables[array_hierarchy]

        table_position = TablePosition.from_table_item(
            table=table, info=info, position=position, line_no=LineCounter.line_no
        )

        array = array_of_tables.get_array(hierarchy=hierarchy)
        array.update_tables(hierarchy=hierarchy, table_position=table_position)

    def get_stylings(self, container_info: ItemInfo, style_info: ItemInfo) -> StylingPositions:
        table_position: TablePosition = self.get_aot_table(hierarchy=style_info.hierarchy)
        if item_is_table(info=container_info):
            styling_positions = table_position.styling
        else:
            styling_positions = table_position.fields[container_info.key].styling
        return styling_positions
    
    def get_array(self, info: ItemInfo) -> FieldPosition:
        """"""
        return self.get_aot_table(hierarchy=info.hierarchy).fields[info.key]


class TableStore(BaseTableStore):
    """"""
    def __init__(self) -> None:
        self._tables: Dict[str, TablePosition] = dict()

    @property
    def hierarchies(self) -> Set[str]:
        """"""
        return set(self._tables.keys())

    def get(self, hierarchy: str) -> TablePosition:
        """"""
        return self._tables[hierarchy]
    
    def contains(self, hierarchy: str) -> bool:
        """"""
        return hierarchy in self._tables

    def update(self, item: items.Item, info: ItemInfo, position: ItemPosition) -> None:
        """"""
        self._tables[info.hierarchy].add_field(
            item=item, info=info, position=position, line_no=LineCounter.line_no
        )

    def add_table(
        self,
        hierarchy: str,
        table: Table,
        info: ItemInfo,
        position: ItemPosition
    ) -> None:
        """"""
        table_position = TablePosition.from_table_item(
            table=table, info=info, position=position, line_no=LineCounter.line_no
        )
        self._tables.update({hierarchy: table_position})

    def get_stylings(self, container_info: ItemInfo, style_info: ItemInfo) -> StylingPositions:
        if item_is_table(info=container_info):
            styling_positions = self._tables[style_info.hierarchy].styling
        else:
            styling_positions = (
                self._tables[style_info.hierarchy].fields[container_info.key].styling
            )
        return styling_positions
    
    def get_array(self, info: ItemInfo) -> FieldPosition:
        """"""
        return self._tables[info.hierarchy].fields[info.key]


class DescriptorStore:
    """"""
    def __init__(self) -> None:
        
        # Structures for storing any attributes occurring in top-level space
        self.document = DocumentStore()

        # Structure for storing any array of tables objects
        self.array_of_tables = ArrayOfTablesStore()

        # Structure for storing any attributes occurring within at least one table
        self.tables = TableStore()

    def _store_choice(self, info: ItemInfo, is_aot: bool) -> BaseStore:
        """"""
        descriptor_store: BaseStore
        item_type: Item = info.item_type.item_type
        if (
            item_type == 'document' or
            not info.hierarchy and item_type in {'array', 'field'}
        ):
            descriptor_store = self.document
        elif is_aot:
            descriptor_store = self.array_of_tables
        else:
            descriptor_store = self.tables

        return descriptor_store

    def update_styling(
        self,
        container_info: ItemInfo,
        style: Stylings,
        style_info: ItemInfo,
        position: ItemPosition,
        is_aot: bool
    ) -> None:
        """"""
        descriptor_store = self._store_choice(info=container_info, is_aot=is_aot)
        styling_positions = descriptor_store.get_stylings(
            container_info=container_info, style_info=style_info
        )
        styling_positions.update_stylings(
            style=style, info=style_info, position=position, line_no=LineCounter.line_no
        )

    def update_field_descriptor(
        self, item: items.Item, info: ItemInfo, position: ItemPosition, is_aot: bool
    ) -> None:
        """"""
        descriptor_store = self._store_choice(info=info, is_aot=is_aot)
        descriptor_store.update(item=item, info=info, position=position)

    def update_array_comment(
        self, array: items.Array, info: ItemInfo, is_aot: bool
    ) -> None:
        """"""
        descriptor_store = self._store_choice(info=info, is_aot=is_aot)
        field_position = descriptor_store.get_array(info=info)
        field_position.update_comment(item=array, line_no=LineCounter.line_no)

    def update_table_descriptor(
        self,
        hierarchy: str,
        container: BodyContainerInOrder,
        container_info: ItemInfo,
        position: ItemPosition,
        is_aot: bool
    ) -> None:
        """"""
        if (
            isinstance(container, items.InlineTable) or
            (isinstance(container, items.Table) and not container.is_super_table())
        ):
            descriptor_store: BaseTableStore
            if is_aot:
                descriptor_store = self.array_of_tables
            else:
                descriptor_store = self.tables

            descriptor_store.add_table(
                hierarchy=hierarchy, table=container, info=container_info, position=position
            )