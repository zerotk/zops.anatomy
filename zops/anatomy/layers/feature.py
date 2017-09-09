from zops.anatomy.layers.tree import merge_dict
from collections import OrderedDict


class FeatureNotFound(KeyError):
    pass


class FeatureAlreadyRegistered(KeyError):
    pass


class AnatomyFeatureRegistry(object):

    feature_registry = OrderedDict()

    @classmethod
    def clear(cls):
        cls.feature_registry = OrderedDict()

    @classmethod
    def get(cls, feature_name):
        """
        Returns a previously registered feature associated with the given feature_name.

        :param str feature_name:
        :return AnatomyFeature:
        """
        try:
            return cls.feature_registry[feature_name]
        except KeyError:
            raise FeatureNotFound(feature_name)
        

    @classmethod
    def register(cls, feature_name, feature):
        """
        Registers a feature instance to a name.

        :param str feature_name:
        :param AnatomyFeature feature:
        """
        if feature_name in cls.feature_registry:
            raise FeatureAlreadyRegistered(feature_name)
        cls.feature_registry[feature_name] = feature

    @classmethod
    def register_from_file(cls, filename):
        from zops.anatomy.yaml import yaml_fom_file

        contents = yaml_fom_file(filename)
        return cls.register_from_contents(contents)

    @classmethod
    def register_from_text(cls, text):
        from zops.anatomy.yaml import yaml_load
        from zops.anatomy.text import dedent

        text = dedent(text)
        contents = yaml_load(text)
        return cls.register_from_contents(contents)

    @classmethod
    def register_from_contents(cls, contents):
        for i_feature in contents['anatomy-features']:
            name = i_feature.pop('name')
            variables = i_feature.pop('variables', OrderedDict())
            feature = AnatomyFeature(name, variables)
            commands = i_feature.pop('commands', [])
            for j_command in commands:

                command = j_command.pop('command', None)
                assert commands is not None, "Missing 'command' entry."

                if command == 'create-file':
                    contents = j_command.pop('contents')
                    feature.create_file(**j_command)
                    if contents:
                        feature.add_file_block(j_command['fileid'], contents)

                elif command == 'add-file-block':
                    feature.add_file_block(**j_command)

                elif command == 'add-variables':
                    feature.add_variables(**j_command)

            if i_feature.keys():
                raise KeyError(i_feature.keys())

            cls.register(name, feature)

    @classmethod
    def tree(cls):
        """
        Returns all files created by the registered features.

        This is part of the helper functions for the end-user. Since the user must know all the file-ids in order to add
        contents to the files we'll need a way to list all files and their IDs.

        :return 3-tupple(str, str, str):
            Returns a tuple containing:
                [0]:    Feature name
                [1]:    File-id
                [2]:    Filename
        """
        result = []
        for i_name, i_feature in cls.feature_registry.items():
            for j_command in i_feature.commands:
                if j_command.command == 'create_file':
                    result.append((i_name, j_command.kwargs['fileid'], j_command.kwargs['filename']))
        return result


class IAnatomyFeature(object):
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

    def apply(self, tree):
        """
        Apply this feature instance in the given anatomy-tree.

        :param AnatomyTree tree:
        """
        raise NotImplementedError()


class AnatomyFeature(IAnatomyFeature):

    class Command(object):

        def __init__(self, command, **kwargs):
            self.command = command
            self.kwargs = kwargs

        def __call__(self, tree):
            func = getattr(tree, self.command)
            return func(**self.kwargs)

        def __str__(self):
            return '{}({})'.format(
                self.command,
                ', '.join(
                    ['{}={}'.format(*i) for i in self.kwargs.items()]
                )
            )

    def __init__(self, name, variables=None):
        super(AnatomyFeature, self).__init__(name)
        self.__commands = []
        self.__variables = OrderedDict()
        self.__variables[name] = variables or OrderedDict()

    def apply(self, tree):
        """
        Implements AnatomyFeature.apply.
        """
        tree.add_variables(self.__variables, left_join=False)
        for i_command in self.__commands:
            i_command(tree)

    @property
    def commands(self):
        return self.__commands

    def list_commands(self):
        """
        List commands as strings for testing.
        """
        return [str(i) for i in self.__commands]

    # Commands

    def create_file(self, fileid, filename, variables=None):
        command = self.Command('create_file', fileid=fileid, filename=filename, variables=variables)
        self.__commands.append(command)

    def add_variables(self, variables):
        command = self.Command('add_variables', variables=variables)
        self.__commands.append(command)

    def add_file_block(self, fileid, contents):
        command = self.Command('add_file_block', fileid=fileid, contents=contents)
        self.__commands.append(command)
