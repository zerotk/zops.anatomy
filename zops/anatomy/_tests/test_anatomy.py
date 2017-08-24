import os

from zops.anatomy.anatomy import AnatomyFile, AnatomyTree, AnatomyFeature


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
    f.apply(datadir)

    # Check
    _assert_file(
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


def test_anatomy_tree(datadir):

    # Prepare
    tree = AnatomyTree()
    tree['.gitignore'].add_block('line 1')
    tree['.gitignore'].add_block('line 2')

    # Execute
    tree.apply(datadir)

    # Check
    _assert_file(
        datadir + '/.gitignore',
        """
            line 1
            line 2
        """
    )


def test_anatomy_feature(datadir):

    class AlphaAnatomyFeature(AnatomyFeature):

        def apply(self, tree):
            tree['.gitignore'].add_block(
                """
                    .pyd
                    .pyc
                """
            )
            tree['pytest.ini'].add_block(
                """
                    [pytest]
                    addopts = --reuse - db - -pylama - -tb = short - -ds
                    ax.projeto.settings
                    timeout = 240
                """
            )

    # Prepare
    tree = AnatomyTree()
    feature = AlphaAnatomyFeature()

    # Execute
    feature.apply(tree)
    tree.apply(datadir)

    # Check
    _assert_file(
        datadir + '/.gitignore',
        """
            .pyd
            .pyc
        """
    )
    _assert_file(
        datadir + '/pytest.ini',
        """
            [pytest]
            addopts = --reuse - db - -pylama - -tb = short - -ds
            ax.projeto.settings
            timeout = 240
        """
    )


def _assert_file(filename, expected):
    from zops.anatomy.text import dedent

    expected = dedent(expected)
    assert os.path.isfile(filename)
    obtained = open(filename, 'r').read()
    assert obtained == expected
