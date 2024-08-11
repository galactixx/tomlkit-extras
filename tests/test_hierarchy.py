from tomlkit_extras import Hierarchy

from tomlkit_extras._hierarchy import standardize_hierarchy

def test_standardize_hierarchy() -> None:
    """"""
    HIERARCHY_TOOL_RUFF = 'tool.ruff'

    hierarchy_tool_ruff = standardize_hierarchy(hierarchy=HIERARCHY_TOOL_RUFF)
    assert hierarchy_tool_ruff == Hierarchy(hierarchy=('tool', ), attribute='ruff')

    hierarchy_tool_ruff_again = standardize_hierarchy(hierarchy=hierarchy_tool_ruff)
    assert hierarchy_tool_ruff_again == hierarchy_tool_ruff


def test_hierarchy() -> None:
    """"""
    hierarchy_tool_ruff = Hierarchy(hierarchy=('tool', ), attribute='ruff')

    assert Hierarchy.from_str_hierarchy(hierarchy='tool.ruff') == 'tool.ruff'

    # Test dunder methods
    assert hierarchy_tool_ruff == 'tool.ruff'
    assert hierarchy_tool_ruff == Hierarchy.from_str_hierarchy(hierarchy='tool.ruff')
    assert repr(hierarchy_tool_ruff) == f'<Hierarchy tool.ruff>'
    assert len(hierarchy_tool_ruff) == 2
    assert str(hierarchy_tool_ruff) == 'tool.ruff'

    # Test properties
    assert hierarchy_tool_ruff.full_hierarchy == ('tool', 'ruff')
    assert hierarchy_tool_ruff.full_hierarchy_str == 'tool.ruff'
    assert hierarchy_tool_ruff.hierarchy_depth == 2
    assert hierarchy_tool_ruff.root_attribute == 'tool'
    assert hierarchy_tool_ruff.base_hierarchy_str == 'tool'
    assert hierarchy_tool_ruff.sub_hierarchies == ['tool', 'tool.ruff']

    # Test class methods
    HIERARCHIES = {'tool', 'tool.ruff.lint', 'tool.rye', 'build-system', 'tool.ruff'}
    shortest_sub_hierarchy = hierarchy_tool_ruff.shortest_sub_hierarchy(hierarchies=HIERARCHIES)
    assert shortest_sub_hierarchy == 'tool'

    longest_sub_hierarchy = hierarchy_tool_ruff.longest_sub_hierarchy(hierarchies=HIERARCHIES)
    assert longest_sub_hierarchy == 'tool.ruff'

    # Test static and other methods
    hierarchy_tool_ruff.add_to_hierarchy(update='lint')
    assert hierarchy_tool_ruff == 'tool.ruff.lint'
    assert hierarchy_tool_ruff.is_child_hierarchy(hierarchy='tool.ruff.lint.per-file-ignores')
    assert not hierarchy_tool_ruff.is_child_hierarchy(hierarchy='tool.ruff.lint.rules.noqa')