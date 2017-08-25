from zops.anatomy.engine import AnatomyFile, AnatomyTree, AnatomyFeature
from zops.anatomy.assertions import assert_file_contents


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
    f = AnatomyFile("{filename}")
    f.add_block('This is alpha.')
    f.apply(datadir, variables={'filename': 'alpha.txt'})
    assert_file_contents(
        datadir + '/alpha.txt',
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
    tree.apply(datadir, variables={})

    # Check
    assert_file_contents(
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
    tree.apply(datadir, variables={})

    # Check
    assert_file_contents(
        datadir + '/.gitignore',
        """
            .pyd
            .pyc
        """
    )
    assert_file_contents(
        datadir + '/pytest.ini',
        """
            [pytest]
            addopts = --reuse - db - -pylama - -tb = short - -ds
            ax.projeto.settings
            timeout = 240
        """
    )
