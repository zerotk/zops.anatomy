import os

from .text import dedent


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


