from tomlkit_extensions.file_validator import load_toml_file
from tomlkit_extensions.descriptor import TOMLDocumentDescriptor

import prettyprinter as pp

toml_document = load_toml_file(
    toml_source=r'C:\Users\12158\Desktop\TOML\table array.toml'
)

table_mapping = TOMLDocumentDescriptor(toml_source=toml_document)

pp.pprint(table_mapping._document_stylings)
pp.pprint(table_mapping._document_lines)
pp.pprint(table_mapping._attribute_lines)
pp.pprint(table_mapping._array_of_tables)

pp.pprint(
    table_mapping.get_styling(
        styling='# this is the first comment for lint table', hierarchy='tool.ruff.lint'
    )
)