from tomlkit import items, TOMLDocument
from tomlkit.container import OutOfOrderTableProxy

DICTIONARY_LIKE_TYPES = (
    TOMLDocument,
    items.Table,
    items.InlineTable,
    OutOfOrderTableProxy
)

INSERTION_TYPES = (
    TOMLDocument,
    items.Table,
    items.InlineTable,
    OutOfOrderTableProxy,
    items.Array
)