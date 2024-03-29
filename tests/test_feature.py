from zops.anatomy.assertions import assert_file_contents
from zops.anatomy.layers.feature import AnatomyFeature, AnatomyFeatureRegistry
from zops.anatomy.layers.tree import AnatomyTree
import os


def test_anatomy_feature(datadir):
    feature = AnatomyFeature("createfile")
    feature.create_file("filename.txt", "# This file is generated by zops.anatomy.")

    _play_feature(feature, datadir)

    assert_file_contents(
        datadir + "/filename.txt",
        """
            # This file is generated by zops.anatomy.
        """,
    )

    # Now, create a link to filename.txt
    feature = AnatomyFeature("createlink")
    feature.create_link("symlink.txt", "filename.txt")

    _play_feature(feature, datadir)

    assert_file_contents(
        datadir + "/symlink.txt",
        """
            # This file is generated by zops.anatomy.
        """,
    )
    assert os.path.islink(datadir + "/symlink.txt")
    assert not os.path.islink(datadir + "/filename.txt")


def test_anatomy_feature_with_variable(datadir):
    feature = AnatomyFeature("CREATEFILE", variables={"code": "ALPHA"})
    feature.create_file(
        "filename.txt",
        "# This file UNKNOWN from feature {{ CREATEFILE.code }}.",
    )
    AnatomyFeatureRegistry.clear()
    assert AnatomyFeatureRegistry.tree() == []
    AnatomyFeatureRegistry.register("CREATEFILE", feature)
    assert AnatomyFeatureRegistry.tree() == [
        ("CREATEFILE", "filename.txt", "filename.txt")
    ]

    # Apply Feature
    tree = AnatomyTree()
    assert tree._AnatomyTree__variables == {}
    feature.apply(tree)
    assert tree._AnatomyTree__variables == {
        "CREATEFILE": {"code": "ALPHA"},
    }
    tree.apply(datadir)

    assert_file_contents(
        datadir + "/filename.txt",
        """
            # This file UNKNOWN from feature ALPHA.
        """,
    )


def test_anatomy_feature_from_yaml(datadir):
    AnatomyFeatureRegistry.clear()
    AnatomyFeatureRegistry.register_from_text(
        """
            anatomy-features:
              - name: CREATEFILE
                variables:
                  code: BRAVO
                create-file:
                  filename: filename.txt
                  contents: |
                     # This file is generated by zops.anatomy.
        """
    )
    assert AnatomyFeatureRegistry.tree() == [
        ("CREATEFILE", "filename.txt", "filename.txt")
    ]

    feature = AnatomyFeatureRegistry.get("CREATEFILE")
    assert feature.filenames() == ["filename.txt"]

    tree = _play_feature(feature, datadir)
    assert tree._AnatomyTree__variables == {
        "CREATEFILE": {"code": "BRAVO"},
    }

    assert_file_contents(
        datadir + "/filename.txt",
        """
            # This file is generated by zops.anatomy.
        """,
    )


def _play_feature(feature, directory, variables={}):
    """
    Could this be on AnatomyPlaybook.play?
    :param feature:
    :param directory:
    """
    tree = AnatomyTree()
    feature.apply(tree)
    tree.apply(directory, variables)
    return tree
