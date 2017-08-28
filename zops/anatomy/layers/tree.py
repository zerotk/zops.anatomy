import os

from zops.anatomy.text import dedent


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

        from jinja2 import Environment, Template
        env = Environment(
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

        def expandit(text_):
            template_ = env.from_string(text_, template_class=Template)
            return template_.render(**variables)

        env.filters['expandit'] = expandit
        result = expandit(text)
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
        self.variables = {}
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

    def apply(self, directory, variables=None):
        """
        Create all registered files.

        :param str directory:
        :param dict variables:
        """
        dd = self.variables.copy()
        if variables is not None:
            dd = merge_dict(dd, variables)

        for i_file in self.__files.values():
            i_file.apply(directory, dd)

    def create_file(self, fileid, filename, variables={}):
        if fileid in self.__files:
            raise FileExistsError(fileid)

        self.__files[fileid] = AnatomyFile(filename)
        self.variables[fileid] = variables
        return None

    def add_file_block(self, fileid, contents):
        if fileid not in self.__files:
            raise FileNotFoundError(fileid)
        file = self.__files[fileid]
        file.add_block(contents)
        return None

    def add_variables(self, variables):
        self.variables = merge_dict(self.variables, variables)
        return None


def merge_dict(a, b, left_join=True):

    def merge_value(v1, v2):
        if v2 is None:
            return v1
        elif isinstance(v1, dict):
            return merge_dict(v1, v2, left_join=False)
        elif isinstance(v1, (list, tuple)):
            return v1 + v2
        else:
            return v2

    if left_join:
        keys = a.keys()
        right_keys = set(b.keys()).difference(set(a.keys()))
        if right_keys:
            raise RuntimeError('Extra keys: {}'.format(right_keys))
    else:
        keys = set(a.keys()).union(set(b.keys()))

    return {i: merge_value(a.get(i), b.get(i)) for i in keys}
