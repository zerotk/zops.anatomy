from zops.anatomy.assertions import assert_file_contents
from zops.anatomy.engine import AnatomyFeature, ProgrammableAnatomyFeature
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
    AnatomyFeature.register_from_file(datadir + '/anatomy-features.yml')
    playbook = AnatomyPlaybook.from_file(datadir + '/anatomy-playbook.yml')

    target_dir = datadir + '/target'
    playbook.apply(target_dir)

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
