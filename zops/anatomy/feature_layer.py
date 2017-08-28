class AnatomyFeatureRegistry(object):

    feature_registry = {}

    @classmethod
    def clear(cls):
        cls.feature_registry = {}

    @classmethod
    def get(cls, feature_name):
        """
        Returns a previously registered feature associated with the given feature_name.

        :param str feature_name:
        :return AnatomyFeature:
        """
        return cls.feature_registry[feature_name]

    @classmethod
    def register(cls, feature_name, feature):
        """
        Registers a feature instance to a name.

        :param str feature_name:
        :param AnatomyFeature feature:
        """
        assert feature_name not in cls.feature_registry
        cls.feature_registry[feature_name] = feature

    @classmethod
    def register_from_file(cls, filename):
        from .yaml import read_yaml

        contents = read_yaml(filename)
        for i_feature in contents['anatomy-features']:
            name = i_feature['name']
            feature = ProgrammableAnatomyFeature(name, i_feature.get('variables', {}))
            items = i_feature['items']
            for j_item in items:

                # Handle add-file-block
                details = j_item.get('add-file-block')
                if details:
                    feature.add_file_block(details['filename'], details['contents'])

                # Handle pytest-ini
                # Handle add-python-dependencies
                # Design Pattern: Strategy (?)

            cls.register(name, feature)


class AnatomyFeature(object):
    """
    Implements a feature. A feature can add content in many files in its 'apply' method.

    Usage:
        tree = AnatomyTree()
        variables = {}

        feature = AnatomyFeatureRegistry.get('alpha')
        feature.apply(tree, variables)

        tree.apply('directory')
    """

    def __init__(self, name):
        self.__name = name

    @property
    def name(self):
        return self.__name

    def get_variables(self):
        raise NotImplementedError()

    def apply(self, tree):
        """
        Apply this feature instance in the given anatomy-tree.

        :param AnatomyTree tree:
        """
        raise NotImplementedError()


class ProgrammableAnatomyFeature(AnatomyFeature):

    class Item(object):

        def __init__(self, filename, contents):
            self.filename = filename
            self.contents = contents

    def __init__(self, name, variables=None):
        super(ProgrammableAnatomyFeature, self).__init__(name)
        self.__items = []
        self.__variables = variables or {}

    def get_variables(self):
        """
        Implements AnatomyFeature.get_variables.
        """
        return self.__variables

    def apply(self, tree):
        """
        Implements AnatomyFeature.apply.
        """
        for i_item in self.__items:
            tree[i_item.filename].add_block(i_item.contents)

    def add_file_block(self, filename, contents):
        item = self.Item(filename, contents)
        self.__items.append(item)
