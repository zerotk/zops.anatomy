from .text import dedent
import os


class TemplateEngine(object):
    """
    Provide an easy and centralized way to change how we expand templates.
    """

    __singleton = None

    @classmethod
    def get(cls):
        if cls.__singleton is None:
            cls.__singleton = cls()
        return cls.__singleton

    def expand(self, text, variables):
        from jinja2 import Template
        template = Template(
            text,
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )
        result = template.render(**variables)

        # other = text.format_map(variables)
        # assert result == other

        return result



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

    def apply(self, directory, variables):
        """
        Create the file using all registered blocks.
        Expand variables in all blocks.

        :param directory:
        :param variables:
        :return:
        """
        filename = os.path.join(directory, self.__filename)

        contents = ''
        for i_block in self.blocks:
            contents += i_block.as_text(variables)
        if not contents.endswith('\n'):
            contents += '\n'

        filename = TemplateEngine.get().expand(filename, variables)
        with open(filename, 'w') as oss:
            oss.write(contents)


class AnatomyFileBlock(object):
    """
    An anatomy-file is composed by many blocks. This class represents one of these blocks.
    """

    def __init__(self, contents):
        self.__contents = contents

    def as_text(self, variables):
        result = TemplateEngine.get().expand(self.__contents, variables)
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

    def apply(self, directory, variables):
        """
        Create all registered files.

        :param str directory:
        :param dict variables:
        """
        for i_file in self.__files.values():
            i_file.apply(directory, variables)


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
