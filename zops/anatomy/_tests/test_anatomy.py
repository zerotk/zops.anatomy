import pytest

from zops.anatomy.assertions import assert_file_contents
from zops.anatomy.layers.feature import AnatomyFeature, AnatomyFeatureRegistry
from zops.anatomy.layers.playbook import AnatomyPlaybook


def test_success(anatomy_checker):
    """
        anatomy-features:
          - name: ALPHA
            variables:
                name: Alpha
            commands:
              - command: create-file
                fileid: alphatxt
                filename: alpha.txt
                contents: |
                    This is {{ ALPHA.name }}.
        anatomy-playbook:
            use-features:
                - ALPHA
        target:
            alpha.txt: |
                This is Alpha.
    """
    anatomy_checker.check(test_success.__doc__)


def test_invalid_key(anatomy_checker):
    """
        anatomy-features:
          - name: ALPHA
            invalid:
              - one
              - two
            variables:
              name: Alpha
            commands:
              - command: create-file
                fileid: alphatxt
                filename: alpha.txt
                contents: |
                  This is {{ ALPHA.name }}.
        anatomy-playbook:
            use-features:
              - ALPHA
        target:
            alpha.txt: |
              This is Alpha.
    """
    with pytest.raises(KeyError):
        anatomy_checker.check(test_invalid_key.__doc__)


def test_use_features(anatomy_checker):
    """
        anatomy-features:
          - name: ALPHA
            commands:
              - command: create-file
                fileid: alphatxt
                filename: alpha.txt
                contents: |
                  This is Alpha.
          - name: BRAVO
            commands:
              - command: create-file
                fileid: bravotxt
                filename: bravo.txt
                contents: |
                  This is Bravo.
          - name: ZULU
            commands:
              - command: add-variables
                variables:
                  ALPHA: {}
                  BRAVO: {}
        anatomy-playbook:
            use-features:
              - ALPHA
              - BRAVO
              - ZULU
        target:
          alpha.txt: |
            This is Alpha.
          bravo.txt: |
            This is Bravo.
    """
    anatomy_checker.check(test_use_features.__doc__)


def test_undefined(anatomy_checker):
    """
        anatomy-features:
          - name: ALPHA
            variables:
                name: Alpha
            commands:
              - command: create-file
                fileid: alphatxt
                filename: alpha.txt
                contents: |
                    This is {{ UNDEFINED }}.
        anatomy-playbook:
            use-features:
                - ALPHA
        target: {}
    """
    with pytest.raises(RuntimeError):
        anatomy_checker.check(test_undefined.__doc__)


@pytest.fixture
def anatomy_checker(datadir):

    class AnatomyChecker(object):
        def check(self, doc):
            from zops.anatomy.yaml import yaml_load
            from zops.anatomy.text import dedent

            text = dedent(doc)
            contents = yaml_load(text)
            AnatomyFeatureRegistry.clear()
            AnatomyFeatureRegistry.register_from_contents(contents)
            playbook = AnatomyPlaybook.from_contents(contents)
            target_dir = datadir + '/target'
            playbook.apply(target_dir)

            for i_filename, i_expected in contents['target'].items():
                assert_file_contents(
                    target_dir.join(i_filename),
                    i_expected
                )

    return AnatomyChecker()
