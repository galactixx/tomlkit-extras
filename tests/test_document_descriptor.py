# def test_toml_b_descriptor() -> None:
#     """"""
#     toml_document: TOMLDocument = load_toml_file(toml_source='./tests/examples/toml_b.toml')
#     document_descriptor = TOMLDocumentDescriptor(toml_source=toml_document)

#     # Basic statistics of the TOML file
#     assert document_descriptor.number_of_aots == 1
#     assert document_descriptor.number_of_arrays == 0
#     assert document_descriptor.number_of_comments == 4
#     assert document_descriptor.number_of_fields == 9
#     assert document_descriptor.number_of_inline_tables == 1
#     assert document_descriptor.number_of_tables == 5

#     # Get comment from the beginning of file
#     styling_descriptors = document_descriptor.get_styling(styling='# this is a document comment')
#     assert len(styling_descriptors) == 1
    
#     styling_descriptor = styling_descriptors[0]
#     _validate_style_descriptor(
#         styling_descriptor,
#         'comment',
#         'document',
#         None,
#         4,
#         3,
#         '# this is a document comment',
#         False
#     )

#     # Get comments from tool.ruff.lint table
#     hierarchy_ruff_lint = Hierarchy.from_str_hierarchy(hierarchy='tool.ruff.lint')
#     ruff_comments_first_descriptors = document_descriptor.get_styling(
#         styling='# this is the first comment for lint table', hierarchy=hierarchy_ruff_lint
#     )
#     assert len(ruff_comments_first_descriptors) == 1

#     ruff_style_first_descriptor = ruff_comments_first_descriptors[0]
#     _validate_style_descriptor(
#         ruff_style_first_descriptor,
#         'comment',
#         'table',
#         hierarchy_ruff_lint,
#         10,
#         1,
#         '# this is the first comment for lint table',
#         False
#     )

#     ruff_comments_second_descriptors = document_descriptor.get_styling(
#         styling='# this is the second comment for lint table', hierarchy=hierarchy_ruff_lint
#     )
#     assert len(ruff_comments_second_descriptors) == 1

#     ruff_style_second_descriptor = ruff_comments_second_descriptors[0]
#     _validate_style_descriptor(
#         ruff_style_second_descriptor,
#         'comment',
#         'table',
#         hierarchy_ruff_lint,
#         11,
#         2,
#         '# this is the second comment for lint table',
#         False
#     )

#     # Field descriptor for document field
#     hierarchy_project = Hierarchy.from_str_hierarchy(hierarchy='project')
#     name_descriptor = document_descriptor.get_field(hierarchy=hierarchy_project)
#     _validate_field_descriptor(
#         name_descriptor,
#         'field',
#         'document',
#         'project',
#         hierarchy_project,
#         1,
#         1,
#         1,
#         'Example Project',
#         None,
#         False
#     )

#     # Field descriptor for tool.ruff table
#     hierarchy_line_length = Hierarchy.from_str_hierarchy(hierarchy='tool.ruff.line-length')
#     line_length_descriptor = document_descriptor.get_field(hierarchy=hierarchy_line_length)
#     _validate_field_descriptor(
#         line_length_descriptor,
#         'field',
#         'table',
#         'line-length',
#         hierarchy_line_length,
#         7,
#         1,
#         1,
#         88,
#         None,
#         False
#     )

#     # Table descriptor for tool.ruff table
#     hieraarchy_ruff = Hierarchy.from_str_hierarchy(hierarchy='tool.ruff')
#     ruff_table_descriptor = document_descriptor.get_table(hierarchy=hieraarchy_ruff)

#     # Validate ruff table descriptor
#     _validate_table_descriptor(
#         ruff_table_descriptor,
#         'table',
#         'super-table',
#         'ruff',
#         hieraarchy_ruff,
#         6,
#         1,
#         1,
#         {'line-length': line_length_descriptor},
#         CommentDescriptor(
#             comment='# this is a tool.ruff comment', line_no=6
#         ),
#         False
#     )

#     # Field descriptor for the convention field within the pydocstyle inline table
#     hierarchy_convention = Hierarchy.from_str_hierarchy(hierarchy='tool.ruff.lint.pydocstyle.convention')
#     descriptor_convention = FieldDescriptor(
#         parent_type='inline-table',
#         name='convention',
#         hierarchy=hierarchy_convention,
#         line_no=12,
#         attribute_pos=1,
#         container_pos=2,
#         comment=None,
#         from_aot=False,
#         item_type='field',
#         value='numpy'
#     )

#     assert document_descriptor.get_field(hierarchy=hierarchy_convention) == descriptor_convention

#     # Table descriptor for the pydocstyle inline table in tool.ruff.lint.pydocstyle
#     hierarchy_pydocstyle = Hierarchy.from_str_hierarchy(hierarchy='tool.ruff.lint.pydocstyle')
#     descriptor_pydocstyle = TableDescriptor(
#         parent_type='table',
#         name='pydocstyle',
#         hierarchy=hierarchy_pydocstyle,
#         line_no=12,
#         attribute_pos=1,
#         container_pos=3,
#         comment=None,
#         from_aot=False,
#         item_type='inline-table',
#         fields={'convention': descriptor_convention},
#         child_tables=None
#     )

#     assert document_descriptor.get_table(hierarchy=hierarchy_pydocstyle) == descriptor_pydocstyle

#     # Field descriptor for the fields within the main_table
#     hierarchy_name = Hierarchy.from_str_hierarchy(hierarchy='main_table.name')
#     descriptor_name = FieldDescriptor(
#         parent_type='table',
#         name='name',
#         hierarchy=hierarchy_name,
#         line_no=15,
#         attribute_pos=1,
#         container_pos=1,
#         comment=None,
#         from_aot=False,
#         item_type='field',
#         value='Main Table'
#     )

#     hierarchy_desc = Hierarchy.from_str_hierarchy(hierarchy='main_table.description')
#     descriptor_desc = FieldDescriptor(
#         parent_type='table',
#         name='description',
#         hierarchy=hierarchy_desc,
#         line_no=16,
#         attribute_pos=2,
#         container_pos=2,
#         comment=None,
#         from_aot=False,
#         item_type='field',
#         value='This is the main table containing an array of nested tables.'
#     )

#     assert document_descriptor.get_field(hierarchy=hierarchy_name) == descriptor_name
#     assert document_descriptor.get_field(hierarchy=hierarchy_desc) == descriptor_desc

#     # Table descriptor for the main_table table
#     hierarchy_main_table = Hierarchy.from_str_hierarchy(hierarchy='main_table')
#     descriptor_main_table = TableDescriptor(
#         parent_type='document',
#         name='main_table',
#         hierarchy=hierarchy_main_table,
#         line_no=14,
#         attribute_pos=3,
#         container_pos=6,
#         comment=None,
#         from_aot=False,
#         item_type='table',
#         fields={'name': descriptor_name, 'description': descriptor_desc},
#         child_tables=None
#     )

#     assert document_descriptor.get_table(hierarchy=hierarchy_main_table) == descriptor_main_table

#     # Field descriptors for main_table.sub_tables array of tables
#     hierarchy_sub_tables_name = Hierarchy.from_str_hierarchy(hierarchy='main_table.sub_tables.name')
#     descriptor_sub_tables_name_one = FieldDescriptor(
#         parent_type='table',
#         name='name',
#         hierarchy=hierarchy_sub_tables_name,
#         line_no=19,
#         attribute_pos=1,
#         container_pos=1,
#         comment=None,
#         from_aot=True,
#         item_type='field',
#         value='Sub Table 1'
#     )
#     descriptor_sub_tables_name_two = FieldDescriptor(
#         parent_type='table',
#         name='name',
#         hierarchy=hierarchy_sub_tables_name,
#         line_no=23,
#         attribute_pos=1,
#         container_pos=1,
#         comment=None,
#         from_aot=True,
#         item_type='field',
#         value='Sub Table 2'
#     )
    
#     assert document_descriptor.get_field_from_array_of_tables(hierarchy=hierarchy_sub_tables_name) == [
#         descriptor_sub_tables_name_one, descriptor_sub_tables_name_two
#     ]

#     hierarchy_sub_tables_value = Hierarchy.from_str_hierarchy(hierarchy='main_table.sub_tables.value')
#     descriptor_sub_tables_value_one = FieldDescriptor(
#         parent_type='table',
#         name='value',
#         hierarchy=hierarchy_sub_tables_value,
#         line_no=20,
#         attribute_pos=2,
#         container_pos=2,
#         comment=None,
#         from_aot=True,
#         item_type='field',
#         value=10
#     )
#     descriptor_sub_tables_value_two = FieldDescriptor(
#         parent_type='table',
#         name='value',
#         hierarchy=hierarchy_sub_tables_value,
#         line_no=24,
#         attribute_pos=2,
#         container_pos=2,
#         comment=None,
#         from_aot=True,
#         item_type='field',
#         value=20
#     )
    
#     assert document_descriptor.get_field_from_array_of_tables(hierarchy=hierarchy_sub_tables_value) == [
#         descriptor_sub_tables_value_one, descriptor_sub_tables_value_two
#     ]

#     # Table descriptors for the main_table.sub_tables
#     hierarchy_sub_tables = Hierarchy.from_str_hierarchy(hierarchy='main_table.sub_tables')
#     descriptor_main_sub_table_one = TableDescriptor(
#         item_type='table',
#         parent_type='array-of-tables',
#         name='sub_tables',
#         hierarchy=hierarchy_sub_tables,
#         line_no=18,
#         attribute_pos=1,
#         container_pos=1,
#         comment=None,
#         from_aot=True,
#         child_tables=None,
#         fields={'name': descriptor_sub_tables_name_one, 'value': descriptor_sub_tables_value_one}
#     )
#     descriptor_main_sub_table_two = TableDescriptor(
#         item_type='table',
#         parent_type='array-of-tables',
#         name='sub_tables',
#         hierarchy=hierarchy_sub_tables,
#         line_no=22,
#         attribute_pos=2,
#         container_pos=2,
#         comment=None,
#         from_aot=True,
#         child_tables=None,
#         fields={'name': descriptor_sub_tables_name_two, 'value': descriptor_sub_tables_value_two}
#     )

#     assert document_descriptor.get_table_from_array_of_tables(hierarchy=hierarchy_sub_tables) == [
#         descriptor_main_sub_table_one, descriptor_main_sub_table_two
#     ]

#     # For the *main_table.sub_tables* array of tables
#     descriptor_main_sub_tables = ArrayOfTablesDescriptor(
#         item_type='array-of-tables',
#         parent_type='table',
#         name='sub_tables',
#         hierarchy=hierarchy_sub_tables,
#         line_no=18,
#         attribute_pos=3,
#         container_pos=4,
#         comment=None,
#         from_aot=False,
#         tables=[descriptor_main_sub_table_one, descriptor_main_sub_table_two]
#     )

#     assert document_descriptor.get_array_of_tables(hierarchy=hierarchy_sub_tables) == [
#         descriptor_main_sub_tables
#     ]


# def test_toml_c_descriptor() -> None:
#     """"""
#     toml_document: TOMLDocument = load_toml_file(toml_source='./tests/examples/toml_c.toml')
#     document_descriptor = TOMLDocumentDescriptor(toml_source=toml_document)

#     # Basic statistics of the TOML file
#     assert document_descriptor.number_of_aots == 0
#     assert document_descriptor.number_of_arrays == 1
#     assert document_descriptor.number_of_comments == 6
#     assert document_descriptor.number_of_fields == 4
#     assert document_descriptor.number_of_inline_tables == 1
#     assert document_descriptor.number_of_tables == 3

#     # Get comment from the beginning of file
#     descriptor_comment = StyleDescriptor(
#         item_type='comment',
#         parent_type='document',
#         style='# this is a document comment',
#         hierarchy=None,
#         line_no=1,
#         container_pos=1,
#         from_aot=False
#     )

#     assert document_descriptor.get_styling(styling='# this is a document comment') == [descriptor_comment]

#     # Field descriptors that exist in the top-level document space
#     hierarchy_project = Hierarchy.from_str_hierarchy(hierarchy='project')
#     descriptor_project = FieldDescriptor(
#         item_type='field',
#         parent_type='document',
#         name='project',
#         hierarchy=hierarchy_project,
#         line_no=3,
#         attribute_pos=1,
#         container_pos=3,
#         comment=None,
#         from_aot=False,
#         value='Example Project'
#     )

#     assert document_descriptor.get_field(hierarchy=hierarchy_project) == descriptor_project

#     # Field descriptor for the convention field within the pydocstyle inline table
#     hierarchy_convention = Hierarchy.from_str_hierarchy(hierarchy='tool.ruff.lint.pydocstyle.convention')
#     descriptor_convention = FieldDescriptor(
#         parent_type='inline-table',
#         name='convention',
#         hierarchy=hierarchy_convention,
#         line_no=9,
#         attribute_pos=1,
#         container_pos=2,
#         comment=None,
#         from_aot=False,
#         item_type='field',
#         value='numpy'
#     )

#     assert document_descriptor.get_field(hierarchy=hierarchy_convention) == descriptor_convention

#     # Table descriptor for the pydocstyle inline table in tool.ruff.lint.pydocstyle
#     hierarchy_pydocstyle = Hierarchy.from_str_hierarchy(hierarchy='tool.ruff.lint.pydocstyle')
#     descriptor_pydocstyle = TableDescriptor(
#         parent_type='table',
#         name='pydocstyle',
#         hierarchy=hierarchy_pydocstyle,
#         line_no=9,
#         attribute_pos=1,
#         container_pos=1,
#         comment=None,
#         from_aot=False,
#         item_type='inline-table',
#         fields={'convention': descriptor_convention},
#         child_tables=None
#     )

#     assert document_descriptor.get_table(hierarchy=hierarchy_pydocstyle) == descriptor_pydocstyle

#     # Get comment from the tool.ruff.lint table
#     hierarchy_ruff_lint = Hierarchy.from_str_hierarchy(hierarchy='tool.ruff.lint')
#     descriptor_lint_comment = StyleDescriptor(
#         item_type='comment',
#         parent_type='table',
#         style='# this is the first comment for lint table',
#         hierarchy=hierarchy_ruff_lint,
#         line_no=11,
#         container_pos=3,
#         from_aot=False
#     )

#     assert document_descriptor.get_styling(
#         styling='# this is the first comment for lint table', hierarchy=hierarchy_ruff_lint
#     ) == [descriptor_lint_comment]

#     # Field descriptor for tool.ruff table
#     hierarchy_line_length = Hierarchy.from_str_hierarchy(hierarchy='tool.ruff.line-length')
#     descriptor_line_length = FieldDescriptor(
#         item_type='field',
#         parent_type='table',
#         name='line-length',
#         hierarchy=hierarchy_line_length,
#         line_no=14,
#         attribute_pos=1,
#         container_pos=1,
#         comment=None,
#         from_aot=False,
#         value=88
#     )

#     assert document_descriptor.get_field(hierarchy=hierarchy_line_length) == descriptor_line_length

#     # Table descriptor for tool.ruff table
#     hierarchy_ruff = Hierarchy.from_str_hierarchy(hierarchy='tool.ruff')
#     descriptor_ruff = TableDescriptor(
#         item_type='table',
#         parent_type='super-table',
#         name='ruff',
#         hierarchy=hierarchy_ruff,
#         line_no=13,
#         attribute_pos=2,
#         container_pos=2,
#         comment=None,
#         from_aot=False,
#         fields={'line-length': descriptor_line_length},
#         child_tables={'tool.ruff.lint'}
#     )

#     assert document_descriptor.get_table(hierarchy=hierarchy_ruff) == descriptor_ruff

#     # Get comment from the tool.ruff table
#     descriptor_ruff_comment = StyleDescriptor(
#         item_type='comment',
#         parent_type='table',
#         style='# this is a tool.ruff comment',
#         hierarchy=hierarchy_ruff,
#         line_no=15,
#         container_pos=2,
#         from_aot=False
#     )

#     assert document_descriptor.get_styling(
#         styling='# this is a tool.ruff comment', hierarchy=hierarchy_ruff
#     ) == [descriptor_ruff_comment]

#     # Descriptors for fields within tool.rye table
#     hierarchy_managed = Hierarchy.from_str_hierarchy(hierarchy='tool.rye.managed')
#     descriptor_managed = FieldDescriptor(
#         parent_type='table',
#         name='managed',
#         hierarchy=hierarchy_managed,
#         line_no=20,
#         attribute_pos=1,
#         container_pos=1,
#         comment=None,
#         from_aot=False,
#         item_type='field',
#         value=True
#     )

#     assert document_descriptor.get_field(hierarchy=hierarchy_managed) == descriptor_managed

#     hierarchy_deps = Hierarchy.from_str_hierarchy(hierarchy='tool.rye.dev-dependencies')
#     descriptor_deps = FieldDescriptor(
#         parent_type='table',
#         name='dev-dependencies',
#         hierarchy=hierarchy_deps,
#         line_no=21,
#         attribute_pos=2,
#         container_pos=2,
#         comment=None,
#         from_aot=False,
#         item_type='array',
#         value=['ruff>=0.4.4', 'mypy>=0.812', 'sphinx>=3.5', 'setuptools>=56.0']
#     )

#     assert document_descriptor.get_field(hierarchy=hierarchy_deps) == descriptor_deps

#     # Descriptor for table tool.rye
#     hierarchy_rye = Hierarchy.from_str_hierarchy(hierarchy='tool.rye')
#     descriptor_rye = TableDescriptor(
#         parent_type='super-table',
#         name='rye',
#         hierarchy=hierarchy_rye,
#         line_no=19,
#         attribute_pos=3,
#         container_pos=3,
#         comment=None,
#         from_aot=False,
#         item_type='table',
#         child_tables=None,
#         fields={'managed': descriptor_managed, 'dev-dependencies': descriptor_deps}
#     )

#     assert document_descriptor.get_table(hierarchy=hierarchy_rye) == descriptor_rye
