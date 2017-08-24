from .text import dedent
import os


class AnatomyFile(object):
    """
    Implements an abstraction of a file composed by blocks.

    Usage:
        f = AnatomyFile('filename.txt')
        f.add_block('first line')
        f.add_block('second line')
        f.apply('directory')
    """

    def __init__(self, filename):
        self.__filename = filename
        self.blocks = []

    def add_block(self, contents):
        contents = dedent(contents)
        if not contents.endswith('\n'):
            contents += '\n'
        self.blocks.append(AnatomyFileBlock(contents))

    def apply(self, directory):
        filename = os.path.join(directory, self.__filename)

        contents = ''
        for i_block in self.blocks:
            contents += i_block.as_text()
        if not contents.endswith('\n'):
            contents += '\n'

        with open(filename, 'w') as oss:
            oss.write(contents)


class AnatomyFileBlock(object):

    def __init__(self, contents):
        self.__contents = contents

    def as_text(self):
        import copy

        result = copy.deepcopy(self.__contents)
        return result


class AnatomyTree(object):
    """
    A collection of anatomy-files.

    Usage:
        tree = AnatomyTree()
        tree['.gitignore'].add_block('.pyc')
        tree.apply('directory')
    """

    def __init__(self):
        self.__files = {}

    def get_file(self, filename):
        """
        Returns a AnatomyFile instance associated with the given filename, creating one if there's none registered.

        :param str filename:
        :return AnatomyFile:
        """
        return self.__files.setdefault(filename, AnatomyFile(filename))

    def __getitem__(self, item):
        """
        Shortcut for get_file.

        :param str item:
        :return AnatomyFile:
        """
        return self.get_file(item)

    def apply(self, directory):
        """
        Create all registered files.

        :param str directory:
        """
        for i_file in self.__files.values():
            i_file.apply(directory)


class AnatomyFeature(object):
    """
    Implements a feature. A feature can add content in many files in its 'apply' method.

    Usage:
        tree = AnatomyTree()

        feature = AnatomyFeature.get('alpha')
        feature.apply(tree)

        tree.apply('directory')
    """

    feature_registry = {}

    def __init__(self):
        pass

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
            feature = ProgrammableAnatomyFeature()
            for j_item in i_feature['items']:
                add_file_block = j_item['add-file-block']
                feature.add_file_block(add_file_block['filename'], add_file_block['contents'])
            cls.register(i_feature['name'], feature)

    @classmethod
    def clear_registry(cls):
        cls.feature_registry = {}

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

    def __init__(self):
        super(ProgrammableAnatomyFeature, self).__init__()
        self.__items = []

    def add_file_block(self, filename, contents):
        item = self.Item(filename, contents)
        self.__items.append(item)

    def apply(self, tree):
        for i_item in self.__items:
            tree[i_item.filename].add_block(i_item.contents)
