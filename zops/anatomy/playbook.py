from munch import Munch

from zops.anatomy.engine import AnatomyTree, AnatomyFeature, AnatomyFeatureRegistry
from .yaml import read_yaml


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
        contents = read_yaml(filename)
        for i_feature in contents['use-features']:
            result.use_feature(i_feature)
        for i_key, i_value in contents.get('variables', {}).items():
            result.set_variable(i_key, i_value)
        return result

    def use_feature(self, feature_name):
        assert feature_name not in self.__features
        self.__features[feature_name] = AnatomyFeatureRegistry.get(feature_name)

    def set_variable(self, key, value):
        """

        NOTE: Not sure we should handle dictionary values to Munch here.

        :param str key:
        :param object value:
        """
        assert key not in self.__variables
        if isinstance(value, dict):
            # NOTE: A dictionary with values accessible using attribute notation.
            value = Munch(**value)

        self.__variables[key] = value

    def apply(self, directory):
        import os

        variables = {}
        tree = AnatomyTree()

        if not os.path.isdir(directory):
            os.makedirs(directory)

        for i_feature_name, i_feature in self.__features.items():
            print('applying anatomy-feature {}'.format(i_feature_name))
            i_feature.apply(tree)
            feature_variables = i_feature.get_variables()
            if feature_variables:
                print('applying anatomy-feature variables:')
                for i_key, i_value in feature_variables.items():
                    print('  {}: {}'.format(i_key, i_value))
                variables[i_feature.name] = Munch(**feature_variables)

        variables.update(self.__variables)

        print('applying anatomy-tree')
        tree.apply(directory, variables)
