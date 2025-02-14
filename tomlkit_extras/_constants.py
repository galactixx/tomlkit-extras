from tomlkit import TOMLDocument, items
from tomlkit.container import OutOfOrderTableProxy

# Tomlkit types that are subclasses of dictionaries
DICTIONARY_LIKE_TYPES = (
    TOMLDocument,
    items.Table,
    items.InlineTable,
    OutOfOrderTableProxy,
)
