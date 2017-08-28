from munch import Munch

from zops.anatomy.layers.feature import AnatomyFeatureRegistry, FeatureNotFound
from zops.anatomy.yaml import yaml_fom_file


class AnatomyPlaybook(object):
    """
    Describes features and variables to apply in a project tree.
    """

    def __init__(self):
        self.__features = {}
        self.__variables = {}

    @classmethod
    def from_file(cls, filename):
        result = cls()
        contents = yaml_fom_file(filename)
        for i_feature in contents['use-features']:
            result.use_feature(i_feature)
        for i_key, i_value in contents.get('variables', {}).items():
            result.set_variable(i_key, i_value)
        return result

    def use_feature(self, feature_name):
        self.__features[feature_name] = AnatomyFeatureRegistry.get(feature_name)

    def set_variable(self, key, value):
        """

        NOTE: Not sure we should handle dictionary values to Munch here.

        :param str key:
        :param object value:
        """
        assert key not in self.__variables
        self.__variables[key] = value

    def apply(self, directory):
        from zops.anatomy.layers.tree import AnatomyTree
        import os

        tree = AnatomyTree()

        if not os.path.isdir(directory):
            os.makedirs(directory)

        for i_feature_name, i_feature in self.__features.items():
            print('applying anatomy-feature {}'.format(i_feature_name))
            i_feature.apply(tree)

        print('applying anatomy-tree')
        tree.apply(directory, self.__variables)
