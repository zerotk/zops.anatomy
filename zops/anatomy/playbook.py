from zops.anatomy.engine import AnatomyTree, AnatomyFeature
from .yaml import read_yaml


class AnatomyPlaybook(object):
    """
    Describes features and variables to apply in a project tree.
    """

    def __init__(self):
        self.__features = []

    @classmethod
    def from_file(cls, filename):
        result = cls()
        contents = read_yaml(filename)
        for i_feature in contents['use-features']:
            result.use_feature(i_feature)
        return result

    def use_feature(self, feature_name):
        self.__features.append(feature_name)

    def apply(self, directory):
        import os

        tree = AnatomyTree()

        if not os.path.isdir(directory):
            os.makedirs(directory)

        for i_feature_name in self.__features:
            feature = AnatomyFeature.get(i_feature_name)
            feature.apply(tree)

        tree.apply(directory)
