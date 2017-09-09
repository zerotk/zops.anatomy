import pytest

from zops.anatomy.assertions import assert_file_contents
from zops.anatomy.layers.feature import AnatomyFeature, AnatomyFeatureRegistry
from zops.anatomy.layers.playbook import AnatomyPlaybook


def test_anatomy_playbook(anatomy_tester):
    anatomy_tester.feature.create_file('gitignore', '.gitignore')
    anatomy_tester.feature.add_file_block('gitignore', '.pyc\n.pyd')
    anatomy_tester.feature.add_file_block('gitignore', '.pyo')
    anatomy_tester.check(('.gitignore', '.pyc\n.pyd\n.pyo\n'))


def test_anatomy_playbook_variables(anatomy_tester):
    anatomy_tester.playbook.set_variable('alpha', {'name': 'HELLO'})
    anatomy_tester.feature.create_file('alpha', 'alpha.txt')
    anatomy_tester.feature.add_file_block('alpha', 'This is {{ alpha.name }}.')
    anatomy_tester.check(
        (
            'alpha.txt',
            'This is HELLO.\n'
        )
    )


@pytest.fixture
def anatomy_tester(datadir):
    """
    Helper class for anatomy tests.

    Configure the simplest case of anatomy, including a feature and a playbook.
    """

    class AnatomyTester(object):

        def __init__(self):
            self.target_dir = datadir + '/target'

            # Create a feature
            self.feature = AnatomyFeature('alpha')

            # Register it
            AnatomyFeatureRegistry.register('alpha', self.feature)

            # Create a playbook that uses the feature
            self.playbook = AnatomyPlaybook()
            self.playbook.use_feature('alpha')

        def check(self, *expected):
            self.playbook.apply(self.target_dir)
            for i_filename, i_contents in expected:
                filename = self.target_dir.join(i_filename)
                assert_file_contents(filename, i_contents)

    AnatomyFeatureRegistry.clear()
    yield AnatomyTester()
