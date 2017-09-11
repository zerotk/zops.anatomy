import os

from zops.anatomy.text import dedent
from collections import OrderedDict


class UndefinedVariableInTemplate(KeyError):
    pass


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

        from jinja2 import Environment, Template, StrictUndefined
        env = Environment(
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
            undefined=StrictUndefined
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
        f = AnatomyFile('filename.txt', 'first line')
        f.apply('directory')
    """

    def __init__(self, filename, contents):
        self.__filename = filename
        self.__contents = dedent(contents)

    def apply(self, directory, variables, filename=None):
        """
        Create the file using all registered blocks.
        Expand variables in all blocks.

        :param directory:
        :param variables:
        :return:
        """
        expand = TemplateEngine.get().expand

        filename = filename or self.__filename
        filename = os.path.join(directory, filename)
        filename = expand(filename, variables)

        try:
            contents = expand(self.__contents, variables)
        except Exception as e:
            raise RuntimeError('ERROR: {}: {}'.format(filename, e))

        _create_file(filename, contents)


def _create_file(filename, contents):
    contents.rstrip('\n')
    contents += '\n'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    try:
        with open(filename, 'w') as oss:
            oss.write(contents)
    except Exception as e:
        raise RuntimeError(e)

# class AnatomyFileBlock(object):
#     """
#     An anatomy-file is composed by many blocks. This class represents one of these blocks.
#     """
#
#     def __init__(self, contents):
#         self.__contents = contents
#
#     def as_text(self, variables):
#         result = TemplateEngine.get().expand(self.__contents, variables)
#         return result


class AnatomyTree(object):
    """
    A collection of anatomy-files.

    Usage:
        tree = AnatomyTree()
        tree.create_file('gitignore', '.gitignore', '.pyc')
        tree.apply('directory')
    """

    def __init__(self):
        self.__variables = OrderedDict()
        self.__files = {}

    def get_file(self, filename):
        """
        Returns a AnatomyFile instance associated with the given filename, creating one if there's none registered.

        :param str filename:
        :return AnatomyFile:
        """
        return self.__files.setdefault(filename, AnatomyFile(filename))

    def apply(self, directory, variables=None):
        """
        Create all registered files.

        :param str directory:
        :param dict variables:
        """
        from jinja2 import UndefinedError

        dd = self.__variables.copy()
        if variables is not None:
            dd = merge_dict(dd, variables)

        for i_fileid, i_file in self.__files.items():
            try:
                filename = dd[i_fileid]['filename']
            except KeyError:
                filename = None
            i_file.apply(directory, variables=dd, filename=filename)

    def create_file(self, fileid, filename, contents, variables=None):
        """
        Create a new file in this tree.

        :param str fileid:
        :param str filename:
        :param str contents:
        :param dict variables:
        """
        if fileid in self.__files:
            raise FileExistsError(fileid)

        self.__files[fileid] = AnatomyFile(filename, contents)
        self.__variables[fileid] = variables or OrderedDict()

    def add_variables(self, variables, left_join=True):
        """
        Adds the given variables to this tree variables.

        :param dict variables:
        :param bool left_join:
            If True, the root keys of the new variables (variables parameters) must already exist in the current
            variables dictionary.
        """
        self.__variables = merge_dict(self.__variables, variables, left_join=left_join)


def merge_dict(a, b, left_join=True):
    import itertools

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
        keys = list(a.keys()) + [i for i in b.keys() if i not in a]

    result = OrderedDict()
    for i_key in keys:
        result[i_key] = merge_value(a.get(i_key), b.get(i_key))
    return result
