# tomlkit-extras
![Tests](https://github.com/galactixx/tomlkit-extras/actions/workflows/continuous_integration.yaml/badge.svg)
[![PyPI version](https://img.shields.io/pypi/v/tomlkit-extras.svg)](https://pypi.org/project/tomlkit-extras/)
[![Python versions](https://img.shields.io/pypi/pyversions/tomlkit-extras.svg)](https://pypi.org/project/tomlkit-extras/)
![PyPI Downloads](https://static.pepy.tech/badge/tomlkit-extras/month)
![PyPI Downloads](https://static.pepy.tech/badge/tomlkit-extras)

**tomlkit-extras** is a Python package that extends the functionality of [tomlkit](https://github.com/sdispater/tomlkit), allowing for advanced manipulation, validation, and introspection of TOML files. This package provides enhanced capabilities for handling comments, nested structures, and other nuanced elements within TOML files.

## 📦 **Installation**

To install tomlkit-extras, run the following command:

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
| **hierarchy**      | `Hierarchy`           | A `Hierarchy` instance representing the full hierarchy of the field. |
| **name**           | `str`                 | The name of the field. |
| **item_type**      | `FieldItem`           | A `FieldItem` instance corresponding to a string literal, either 'field' or 'array'. |
| **parent_type**    | `ParentItem` \| `None`| A `ParentItem` instance corresponding to a string literal representing the type of the parent of the structure. Can be None if there is no parent. |
| **line_no**        | `int`                 | An integer line number marking the beginning of the structure. |
| **attribute_position** | `int`              | An integer position of the structure amongst all other key-value pairs (fields, tables) within the parent. |
| **container_position** | `int`               | An integer position of the structure amongst all types, including stylings (whitespace, comments), within the parent. |
| **comment**        | `CommentDescriptor` \| `None` | A `CommentDescriptor` instance corresponding to the comment associated with the structure. Can be None if there is no comment. |
| **value**          | `Any`                 | The value of the field. |
| **value_type**     | `Type[Any]`           | The type of the field value. |
| **stylings**       | `StylingDescriptors`  | An object with all stylings associated with the field. |
| **from_aot**       | `bool`                | A boolean indicating whether the field is nested within an array of tables. |

```python
# Retrieve a specific table
table = descriptor.get_table(hierarchy='table1')
```

**Return Type:** `TableDescriptor`

| **Attribute**    | **Type**          | **Description** |
|-----------------|------------------|-----------------|
| **hierarchy**        | `Hierarchy`            | A `Hierarchy` instance representing the full hierarchy of the table. |
| **name**             | `str`                  | The name of the table. |
| **item_type**        | `TableItem`            | A `TableItem` instance corresponding to a string literal, either 'table' or 'inline-table'. |
| **parent_type**      | `ParentItem` \| `None` | A `ParentItem` instance corresponding to a string literal representing the type of the parent of the structure. Can be None if there is no parent. |
| **line_no**          | `int`                  | An integer line number marking the beginning of the table. |
| **attribute_position** | `int`                | An integer position of the structure amongst all other key-value pairs (fields, tables) within the parent. |
| **container_position** | `int`                 | An integer position of the structure amongst all types, including stylings (whitespace, comments), within the parent. |
| **comment**          | `CommentDescriptor` \| `None` | A `CommentDescriptor` instance corresponding to the comment associated with the structure. Can be None if there is no comment. |
| **fields**           | `Dict[str, FieldDescriptor]` | A dictionary of key-value pairs, each being a field contained in the table. |
| **num_fields**       | `int`                  | The number of fields contained in the table. |
| **stylings**         | `StylingDescriptors`   | An object with all stylings appearing within the table. |
| **from_aot**         | `bool`                 | A boolean indicating whether the table is nested within an array of tables. |

```python
# Retrieve a specific AoT
aots = descriptor.get_aot(hierarchy='array_of_tables')
```

**Return Type:** `List[AoTDescriptor]`

| **Attribute** | **Type**            | **Description** |
|--------------|-------------------|-----------------|
| **hierarchy**        | `Hierarchy`                  | A `Hierarchy` instance representing the full hierarchy of the array. |
| **name**             | `str`                        | The name of the array of tables. |
| **item_type**        | `AoTItem`                    | An `AoTItem` instance, the literal 'array-of-tables'. |
| **parent_type**      | `ParentItem` \| `None`       | A `ParentItem` instance corresponding to a string literal representing the type of the parent of the structure. Can be None if there is no parent. |
| **line_no**          | `int`                        | An integer line number marking the beginning of the array of tables. |
| **attribute_position** | `int`                      | An integer position of the structure amongst all other key-value pairs (fields, tables) within the parent. |
| **container_position** | `int`                      | An integer position of the structure amongst all types, including stylings (whitespace, comments), within the parent. |
| **tables**           | `List[TableDescriptor]`     | A list of `TableDescriptor` instances where each one represents a table within the array of tables. |
| **from_aot**         | `bool`                       | A boolean indicating whether the array is nested within an array of tables. |

```python
# Get all comments from the top-level
stylings = descriptor.get_top_level_stylings(styling='comment')
```

**Return Type:** `List[StyleDescriptor]`

| **Attribute**   | **Type**          | **Description** |
|----------------|------------------|-----------------|
| **hierarchy**        | `Hierarchy` \| `None`  | A `Hierarchy` instance representing the full hierarchy of the styling, or None if it is a top-level styling. |
| **item_type**        | `StyleItem`            | A `StyleItem` instance corresponding to a string literal, either 'whitespace' or 'comment'. |
| **parent_type**      | `ParentItem` \| `None` | A `ParentItem` instance corresponding to a string literal representing the type of the parent of the structure. Can be None if there is no parent. |
| **line_no**          | `int`                  | An integer line number marking the beginning of the styling. |
| **container_position** | `int`                 | An integer position of the structure amongst all types, including stylings (whitespace, comments), within the parent. |
| **style**            | `str`                  | The string representation of the styling. |
| **from_aot**         | `bool`                 | A boolean indicating whether the styling is nested within an array of tables. |

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


### **Using Provided Functions**

### **Comments**

#### **`get_comments` Function**

```python
from tomlkit_extras import get_comments

# Example usage
comments = get_comments(toml_doc, hierarchy=None)
```

**Return Type:** `List[ContainerComment]` \| `None`

Where `ContainerComment` is a **tuple** with the following objects:

| **Index**         | **Type**           | **Description** |
|---------------------|-------------------|-----------------|
| **0**      | `int`             | The line number where the comment is located. |
| **1**          | `str`             | The content of the comment. |

#### **`get_array_field_comment` Function**

```python
from tomlkit_extras import get_array_field_comment

# Example usage
comment = get_array_field_comment(array, array_item)
```

**Return Type:** `str` \| `None`

| **Type**           | **Description** |
|-------------------|-----------------|
| `str` \| `None`             | The comment associated with the array item. Can be None if the array item does not exist. |

### **Deletion**

#### **`delete_from_toml_source` Function**

```python
from tomlkit_extras import delete_from_toml_source

# Example usage
delete_from_toml_source('table1.key1', toml_doc)
```

**Return Type:** `None`

This will delete the key `key1` from the table `[table1]` within the provided TOML document. The deletion will cascade backwards to remove any empty structures left behind as a result of this deletion.

### **Insertion**

```python
from tomlkit_extras import load_toml_file

# Sample TOML content
raw_toml = """ 
[table1] 
# This comment separates the first field
key1 = "value1" 

# This comment separates the second field
key2 = "value2" 
"""

# Load the TOML into a TOMLDocument
toml_doc = load_toml_file(raw_toml)
```

#### **`general_insert` Function**

```python
from tomlkit_extras import general_insert

# Example usage
general_insert(toml_doc, 'some_value', 'table1', 'some_key')
```

**Return Type:** `None`

This will insert a new key-value pair `some_key = "some_value"` into the `[table1]` table, at the bottom after all other fields and comments.

#### **`attribute_insert` Function**

```python
from tomlkit_extras import attribute_insert

# Example usage
attribute_insert(toml_doc, 'some_value', 2, 'table1', 'some_key')
```

**Return Type:** `None`

This will insert a new key-value pair `some_key = "some_value"` at position 2 within the `[table1]` table. This position is relative to other fields appearing within `[table1]`. Thus, the new field would appear between `key1` and `key2`.

#### **`container_insert` Function**

```python
from tomlkit_extras import container_insert

# Example usage
container_insert(toml_doc, 'some_value', 2, 'table1', 'some_key')
```

**Return Type:** `None`

This will insert a new key-value pair `some_key = "some_value"` at position 2 within the `[table1]` table. This position is relative to other fields and stylings (comments and whitespaces) appearing within `[table1]`. Thus, the new field would appear between the comment `# This comment separates the first field` and `key1`.

### **Out-of-Order**

#### **`fix_out_of_order_table` Function**

```python
from tomlkit_extras import fix_out_of_order_table

# Example usage
fixed_table = fix_out_of_order_table(out_of_order_table)
```

**Return Type:** `items.Table`

| **Type**           | **Description** |
|-------------------|-----------------|
| `items.Table`     | The re-ordered TOML table. |

#### **`fix_out_of_order_tables` Function**

```python
from tomlkit_extras import fix_out_of_order_tables

# Example usage
fix_out_of_order_tables(toml_doc)
```

**Return Type:** `None`

This will re-order all out-of-order tables in the provided TOML document. The changes are applied in-place.

### **Retrieval**

#### **`get_positions` Function**

```python
from tomlkit_extras import get_positions

# Example usage
attribute_pos, container_pos = get_positions('table1.key1', toml_doc)
```

**Return Type:** `Tuple[int, int]`

| **Index**         | **Type**           | **Description** |
|---------------------|-------------------|-----------------|
| **0**    | `int`             | The position of the item among key-value pairs in the container. |
| **1**    | `int`             | The position of the item among all container elements (including comments and whitespace). |

#### **`get_attribute_from_toml_source` Function**

```python
from tomlkit_extras import get_attribute_from_toml_source

# Example usage
attribute = get_attribute_from_toml_source('table1.key1', toml_doc)
```

**Return Type:** `Retrieval`

| **Type**           | **Description** |
|-------------------|-----------------|
| `Retrieval`       | The retrieved TOML item, which could be an Item, a Proxy, or a list of Items. |

#### **`is_toml_instance` Function**

```python
from tomlkit_extras import is_toml_instance

# Example usage
is_instance = is_toml_instance(str, 'table1.key1', toml_doc)
```

**Return Type:** `bool`

| **Type**           | **Description** |
|-------------------|-----------------|
| `bool`            | Indicates if the TOML item at the specified hierarchy is of the given type. |

### **Update**

#### **`update_toml_source` Function**

```python
from tomlkit_extras import update_toml_source

# Example usage
update_toml_source(toml_doc, {"key1": "some_value"}, 'table1')
```

**Return Type:** `None`

This will update the `key1` within `[table1]` to have the value `some_value`. The update will be done in place.

## 🔮 **Future Features**

- **TOML Modification**: Provide an extension to the `TOMLDocumentDescriptor` class for modification of structures while maintaining the fast lookup that is already provided.
- **Advanced Comment Handling**: Ability to modify and move comments programmatically.

## 🤝 **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## 📞 **Contact**

If you have any questions or need support, feel free to reach out by opening an issue on the [GitHub repository](#).

