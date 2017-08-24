from zops.anatomy.assertions import assert_file_contents
from zops.anatomy.engine import AnatomyFeature
from zops.anatomy.playbook import AnatomyPlaybook


def test_anatomy_playbook(datadir):
    """
    Tests anatomy-playbook as a class.
    """
    _configure_features()

    playbook = AnatomyPlaybook()
    playbook.use_feature('alpha')

    _execute_and_check(datadir, playbook)


def test_anatomy_playbook_file(datadir):
    """
    Tests anatomy-playbook as a class.
    """
    _configure_features()

    playbook = AnatomyPlaybook.from_file(datadir + '/ansible-playbook.yml')

    _execute_and_check(datadir, playbook)


def _execute_and_check(datadir, playbook):
    # Execute
    target_dir = datadir + '/target'
    playbook.apply(target_dir)

    # Check
    assert_file_contents(
        target_dir + '/.gitignore',
        """
            .pyc
        """
    )
    assert_file_contents(
        target_dir + '/pytest.ini',
        """
            [pytest]
            timeout = 240
        """
    )


def _configure_features():

    class ProgrammableAnatomyFeature(AnatomyFeature):

        class Item(object):

            def __init__(self, filename, contents):
                self.filename = filename
                self.contents = contents

        def __init__(self):
            super(ProgrammableAnatomyFeature, self).__init__()
            self.__items = []

        def add_file_block(self, filename, contents):
            item = self.Item(filename, contents)
            self.__items.append(item)

        def apply(self, tree):
            for i_item in self.__items:
                tree[i_item.filename].add_block(i_item.contents)

    AnatomyFeature.clear_registry()

    feature = ProgrammableAnatomyFeature()
    feature.add_file_block(
        '.gitignore',
        """
            .pyc
        """
    )
    feature.add_file_block(
        'pytest.ini',
        """
            [pytest]
            timeout = 240
        """
    )
    AnatomyFeature.register('alpha', feature)
