from zops.anatomy.tree_layer import AnatomyTree
from zops.anatomy.feature_layer import AnatomyFeature
from zops.anatomy.assertions import assert_file_contents


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
    feature = AlphaAnatomyFeature('alpha')

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


def test_anatomy_feature_variables(datadir):
    from munch import Munch

    class AlphaAnatomyFeature(AnatomyFeature):

        def get_variables(self):
            return {
                'name': 'ALPHA',
            }

        def apply(self, tree):
            tree['alpha.txt'].add_block(
                """This is {{alpha.name}}."""
            )

    # Prepare
    variables = {}
    tree = AnatomyTree()

    feature = AlphaAnatomyFeature('alpha')

    # feature.add_variables(variables)
    m = Munch()
    m[feature.name] = Munch(**feature.get_variables())
    variables.update(m)

    # Execute
    feature.apply(tree)
    tree.apply(datadir, variables=variables)

    # Check
    assert_file_contents(
        datadir + '/alpha.txt',
        """
            This is ALPHA.
        """
    )
