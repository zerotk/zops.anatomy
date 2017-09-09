import pytest

from zops.anatomy.assertions import assert_file_contents
from zops.anatomy.layers.tree import AnatomyFile, AnatomyTree, merge_dict

import os


def test_anatomy_file(datadir):

    # Prepare
    f = AnatomyFile('gitignore')
    f.add_block(
        """
            a
            b
        """
    )
    f.add_block('c\nd\n')
    f.add_block('e\nf')

    # Execute
    f.apply(datadir, variables={})

    # Check
    assert_file_contents(
        datadir + '/gitignore',
        """
            a
            b
            c
            d
            e
            f
        """
    )


def test_anatomy_file_with_filenames_using_variables(datadir):
    f = AnatomyFile("{{filename}}")
    f.add_block('This is alpha.')
    f.apply(datadir, variables={'filename': 'alpha.txt'})
    assert_file_contents(
        datadir + '/alpha.txt',
        """
            This is alpha.
        """
    )


def test_anatomy_file_replace_filename_with_variable(datadir):
    f = AnatomyFile("alpha.txt")
    f.add_block('This is alpha.')
    f.apply(datadir, variables={}, filename='zulu.txt')
    assert not os.path.isfile(datadir + '/alpha.txt')
    assert_file_contents(
        datadir + '/zulu.txt',
        """
            This is alpha.
        """
    )


def test_anatomy_tree(datadir):

    # Prepare
    tree = AnatomyTree()
    tree['.gitignore'].add_block('line 1')
    tree['.gitignore'].add_block('line 2')

    # Execute
    tree.apply(datadir)

    # Check
    assert_file_contents(
        datadir + '/.gitignore',
        """
            line 1
            line 2
        """
    )


def test_anatomy_tree_with_variables(datadir):

    # Prepare
    tree = AnatomyTree()
    tree['alpha.txt'].add_block('This is {{ name }}.')

    # Without defined variables
    with pytest.raises(RuntimeError):
        tree.apply(datadir)

    # With defined variables
    tree.add_variables(
        {'name': 'ALPHA'},
        left_join=False
    )
    tree.apply(datadir)
    assert_file_contents(
        datadir + '/alpha.txt',
        """
            This is ALPHA.
        """
    )


def test_merge_dict():
    # We can add only KEYS that already exists on 'a'.
    with pytest.raises(RuntimeError):
        assert merge_dict(
            dict(a=1),
            dict(b=2)
        )

    with pytest.raises(RuntimeError):
        assert merge_dict(
            dict(a=1),
            dict(b=2),
            left_join=True
        )

    assert merge_dict(
        dict(a=1),
        dict(b=2),
        left_join=False
    ) == dict(a=1, b=2)

    assert merge_dict(
        dict(a=dict(a=1)),
        dict(a=dict(b=2)),
    ) == dict(a=dict(a=1, b=2))

    assert merge_dict({'a': 1}, {'a': 2}) == {'a': 2}
    assert merge_dict({'a': [1]}, {'a': [2]}) == {'a': [1, 2]}
    assert merge_dict({'a': {'aa': [1]}}, {'a': {'aa': [2]}}) == {'a': {'aa': [1, 2]}}
    assert merge_dict(
        {'a': {'aa': [1]}},
        {'a': {'aa': [2]}}
    ) == {'a': {'aa': [1, 2]}}
    assert merge_dict(
        {'PROJECT': {'code_name': 'alpha'}},
        {'PROJECT': {'code_name': 'zulu'}}
    ) == {'PROJECT': {'code_name': 'zulu'}}
