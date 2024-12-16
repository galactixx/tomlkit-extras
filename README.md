# tomlkit-extras
![Tests](https://github.com/galactixx/tomlkit-extras/actions/workflows/continuous_integration.yaml/badge.svg)

**TOMLKit Extras** is a Python package that extends the functionality of [TOMLKit](https://github.com/sdispater/tomlkit), allowing for advanced manipulation, validation, and introspection of TOML files. This package provides enhanced capabilities for handling comments, nested structures, and other nuanced elements within TOML files.

## 📦 **Installation**

To install TOMLKit Extras, run the following command:

```bash
pip install tomlkit-extras
```

## 🚀 **Features**

- **Comment Handling**: Introspect, modify, or retain comments within TOML files.
- **Nested Structure Support**: Access, edit, and validate deeply nested tables and arrays.
- **Validation Tools**: Validate and ensure the integrity of TOML file structures.
- **Enhanced Introspection**: Retrieve metadata and structure details from TOML documents.
- **Comprehensive Field Retrieval**: Extract and modify TOML fields and their properties.

## 📚 **Usage**

### **Using `TOMLDocumentDescriptor`**

The `TOMLDocumentDescriptor` class provides powerful tools for parsing and extracting elements from a TOML document. It can be used to retrieve statistics, extract specific fields, tables, or array-of-tables, and analyze document stylings.

Below are examples showcasing some of the methods available in the  `TOMLDocumentDescriptor` class.

#### **Example Usage**

```python
from tomlkit_extras import TOMLDocumentDescriptor, load_toml_file

# Sample TOML content
raw_toml = """ 
# This is a top-level comment explaining the TOML file
# It provides context about the file's purpose

[table1] 
key1 = "value1" 
key2 = "value2" 

[[array_of_tables]] 
name = "first" 

[[array_of_tables]] 
name = "second" 
"""

# Load the TOML into a TOMLDocument
toml_doc = load_toml_file(raw_toml)

# Initialize the descriptor
descriptor = TOMLDocumentDescriptor(toml_doc)
```

```python
# Access the number of tables appearing in the TOML document
num_tables = descriptor.number_of_tables
```

**Return Type:** `int`

| **Description** |
|-----------------|
| The total number of tables in the TOML document. |

```python
# Access the number of array-of-tables appearing in the TOML document
num_aots = descriptor.number_of_aots
```

**Return Type:** `int`

| **Description** |
|-----------------|
| The total number of array of tables in the TOML document. |

```python
# Retrieve a specific field
field = descriptor.get_field(hierarchy='table1.key1')
```

**Return Type:** `FieldDescriptor`

| **Attribute**       | **Type**               | **Description** |
|-------------------|-----------------------|-----------------|
| **hierarchy**      | `Hierarchy`           | A `Hierarchy` instance representing the full hierarchy of the structure. |
| **name**           | `str`                 | The name of the attribute (field, table, or array of tables). |
| **item_type**      | `FieldItem`           | A `FieldItem` instance corresponding to a string literal representing the type of the table, being either 'field' or 'array'. |
| **parent_type**    | `ParentItem` \| `None`| A `ParentItem` instance corresponding to a string literal representing the type of the parent of the structure. Can be None if there is no parent. |
| **line_no**        | `int`                 | An integer line number marking the beginning of the structure. |
| **attribute_position** | `int`              | An integer position of the structure amongst all other key-value pairs (fields, tables) within the parent. |
| **container_position** | `int`               | An integer position of the structure amongst all other types, including stylings (whitespace, comments), within the parent. |
| **comment**        | `CommentDescriptor` \| `None` | A `CommentDescriptor` instance corresponding to the comment associated with the structure. Can be None if there is no comment. |
| **value**          | `Any`                 | The value of the field. |
| **value_type**     | `Type[Any]`           | The type of the field value. |
| **stylings**       | `StylingDescriptors`  | An object with all stylings associated with the field. |
| **from_aot**       | `bool`                | A boolean indicating whether the structure is nested within an array of tables. |

```python
# Retrieve a specific table
table = descriptor.get_table(hierarchy='table1')
```

**Return Type:** `TableDescriptor`

| **Attribute**    | **Type**          | **Description** |
|-----------------|------------------|-----------------|
| **hierarchy**        | `Hierarchy`            | A `Hierarchy` instance representing the full hierarchy of the structure. |
| **name**             | `str`                  | The name of the attribute (field, table, or array of tables). |
| **item_type**        | `TableItem`            | A `TableItem` instance corresponding to a string literal representing the type of the table, being either 'table' or 'inline-table'. |
| **parent_type**      | `ParentItem` \| `None` | A `ParentItem` instance corresponding to a string literal representing the type of the parent of the structure. Can be None if there is no parent. |
| **line_no**          | `int`                  | An integer line number marking the beginning of the table. |
| **attribute_position** | `int`                | An integer position of the structure amongst all other key-value pairs (fields, tables) within the parent. |
| **container_position** | `int`                 | An integer position of the structure amongst all other types, including stylings (whitespace, comments), within the parent. |
| **comment**          | `CommentDescriptor` \| `None` | A `CommentDescriptor` instance corresponding to the comment associated with the structure. Can be None if there is no comment. |
| **fields**           | `Dict[str, FieldDescriptor]` | A dictionary of key-value pairs, each being a field contained in the table. |
| **num_fields**       | `int`                  | The number of fields contained in the table. |
| **stylings**         | `StylingDescriptors`   | An object with all stylings appearing within the table. |
| **from_aot**         | `bool`                 | A boolean indicating whether the structure is nested within an array of tables. |

```python
# Retrieve a specific AoT
aots = descriptor.get_aot(hierarchy='array_of_tables')
```

**Return Type:** `List[AoTDescriptor]`

| **Attribute** | **Type**            | **Description** |
|--------------|-------------------|-----------------|
| **hierarchy**        | `Hierarchy`                  | A `Hierarchy` instance representing the full hierarchy of the structure. |
| **name**             | `str`                        | The name of the attribute (field, table, or array of tables). |
| **item_type**        | `AoTItem`                    | A `AoTItem` instance corresponding to a string literal representing the structure type. |
| **parent_type**      | `ParentItem` \| `None`       | A `ParentItem` instance corresponding to a string literal representing the type of the parent of the structure. Can be None if there is no parent. |
| **line_no**          | `int`                        | An integer line number marking the beginning of the array of tables. |
| **attribute_position** | `int`                      | An integer position of the structure amongst all other key-value pairs (fields, tables) within the parent. |
| **container_position** | `int`                      | An integer position of the structure amongst all other types, including stylings (whitespace, comments), within the parent. |
| **tables**           | `List[TableDescriptor]`     | A list of `TableDescriptor` instances where each one represents a table within the array of tables. |
| **from_aot**         | `bool`                       | A boolean indicating whether the structure is nested within an array of tables. |

```python
# Get all comments from the top-level
stylings = descriptor.get_top_level_stylings(styling='comment')
```

**Return Type:** `List[StyleDescriptor]`

| **Attribute**   | **Type**          | **Description** |
|----------------|------------------|-----------------|
| **hierarchy**        | `Hierarchy` \| `None`  | A `Hierarchy` instance representing the full hierarchy of the structure, or None if it is a top-level styling. |
| **item_type**        | `StyleItem`            | A `StyleItem` instance corresponding to a string literal representing the type of the styling, being either 'whitespace' or 'comment'. |
| **parent_type**      | `ParentItem` \| `None` | A `ParentItem` instance corresponding to a string literal representing the type of the parent of the structure. Can be None if there is no parent. |
| **line_no**          | `int`                  | An integer line number marking the beginning of the styling. |
| **container_position** | `int`                 | An integer position of the structure amongst all other types, including stylings (whitespace, comments), within the parent. |
| **style**            | `str`                  | The string value of the style. |
| **from_aot**         | `bool`                 | A boolean indicating whether the structure is nested within an array of tables. |

#### **`TOMLDocumentDescriptor` Properties**

- **`number_of_tables`**: Returns the number of tables in the TOML document.
- **`number_of_inline_tables`**: Returns the number of inline tables in the TOML document.
- **`number_of_aots`**: Returns the number of array-of-tables in the TOML document.
- **`number_of_arrays`**: Returns the number of arrays in the TOML document.
- **`number_of_comments`**: Returns the number of comments in the TOML document.
- **`number_of_fields`**: Returns the number of non-array fields in the TOML document.

#### **`TOMLDocumentDescriptor` Methods**

- **`get_field_from_aot(hierarchy)`**: Retrieves all fields from an array-of-tables at a given hierarchy.
- **`get_table_from_aot(hierarchy)`**: Retrieves all tables from an array-of-tables at a given hierarchy.
- **`get_aot(hierarchy)`**: Retrieves all array-of-tables at a given hierarchy.
- **`get_field(hierarchy)`**: Retrieves a field descriptor corresponding to a specific hierarchy.
- **`get_table(hierarchy)`**: Retrieves a table descriptor corresponding to a specific hierarchy.
- **`get_top_level_stylings(styling=None)`**: Retrieves top-level stylings such as comments or whitespace.
- **`get_stylings(styling, hierarchy=None)`**: Retrieves specific stylings, either whitespace or comments, at a specific hierarchy.

## 🤝 **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## 📞 **Contact**

If you have any questions or need support, feel free to reach out by opening an issue on the [GitHub repository](#).

