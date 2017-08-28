import pytest

from zops.anatomy.assertions import assert_file_contents
from zops.anatomy.feature_layer import ProgrammableAnatomyFeature, AnatomyFeatureRegistry
from zops.anatomy.playbook_layer import AnatomyPlaybook


def test_anatomy_playbook(anatomy_tester):
    anatomy_tester.feature.add_file_block(
        '.gitignore',
        '.pyc\n.pyd'
    )
    anatomy_tester.feature.add_file_block(
        '.gitignore',
        '.pyo'
    )
    anatomy_tester.check(
        (
            '.gitignore',
            '.pyc\n.pyd\n.pyo\n'
        )
    )


def test_anatomy_playbook_variables(anatomy_tester):
    anatomy_tester.playbook.set_variable(
        'project',
        {
            'name': 'ALPHA'
        }
    )
    anatomy_tester.feature.add_file_block(
        'alpha.txt',
        'This is {{project.name}}.'
    )
    anatomy_tester.check(
        (
            'alpha.txt',
            'This is ALPHA.\n'
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
            self.feature = ProgrammableAnatomyFeature('alpha')

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


def test_integration(datadir):
    """
    Tests all elements of Anatomy in a setting similar to production, that is, using feature and playbook files.
    """
    AnatomyFeatureRegistry.register_from_file(datadir + '/anatomy-features.yml')
    playbook = AnatomyPlaybook.from_file(datadir + '/anatomy-playbook.yml')

    target_dir = datadir + '/target'
    playbook.apply(target_dir)

    assert_file_contents(
        target_dir + '/README.md',
        """
            # This is Alpha.

            The code is at `alpha`.

            Global is YES.
        """
    )

    assert_file_contents(
        target_dir + '/.gitignore',
        """
            /.idea/
            /.project/
            .pyc
            .pyd
            .pyo
        """
    )

    assert_file_contents(
        target_dir + '/pytest.ini',
        """
            [pytest]
            timeout = 100
        """
    )
