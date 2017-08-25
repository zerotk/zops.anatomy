from zops.anatomy.engine import AnatomyTree, AnatomyFeature
from .yaml import read_yaml


class AnatomyPlaybook(object):
    """
    Describes features and variables to apply in a project tree.
    """

    def __init__(self):
        self.__features = []
        self.__variables = {}

    @classmethod
    def from_file(cls, filename):
        result = cls()
        contents = read_yaml(filename)
        for i_feature in contents['use-features']:
            result.use_feature(i_feature)
        return result

    def use_feature(self, feature_name):
        self.__features.append(feature_name)

    def set_variable(self, key, value):
        """

        NOTE: Not sure we should handle dictionary values to Munch here.

        :param str key:
        :param object value:
        """
        from munch import Munch

        assert key not in self.__variables
        if isinstance(value, dict):
            # NOTE: A dictionary with values accessible using attribute notation.
            value = Munch(**value)

        self.__variables[key] = value

    def apply(self, directory):
        import os

        tree = AnatomyTree()

        if not os.path.isdir(directory):
            os.makedirs(directory)

        for i_feature_name in self.__features:
            feature = AnatomyFeature.get(i_feature_name)
            feature.apply(tree)

        tree.apply(directory, self.__variables)
