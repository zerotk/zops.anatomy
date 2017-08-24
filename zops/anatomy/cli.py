# -*- coding: utf-8 -*-
import os
from zerotk.zops import Console
from .anatomy import Anatomy

import click


ANATOMY_FILENAME = 'anatomy.yml'


click.disable_unicode_literals_warning = True


@click.group('anatomy')
def main():
    pass


@main.command()
@click.argument('directories', nargs=-1)
@click.pass_context
def apply(ctx, directories):
    """
    Apply ax.anatomy templates, loading anatomy.yml file for variables and the list of files to generate.
    """

    def expandit(text, variables_):
        """
        Expands variables in the given text.

        Returns the text with the variables expanded.

        :param str text:
        :param dict variables_:
        :return str:
        """
        from jinja2 import Template
        template = Template(text)
        return template.render(**variables_)

    def read_template_file(filename, template):
        """
        Loads the contents of a file for a template.

        :param str filename:
        :param str template:
        :return str:
        """
        file_path = os.path.join(os.path.dirname(__file__), 'etc', 'templates', template, filename)
        # check if a specific template exists, else fallback to default
        if not os.path.exists(file_path):
            file_path = os.path.join(os.path.dirname(__file__), 'etc', 'templates', 'default', filename)

        with open(file_path, 'r') as iss:
            result = iss.read()
        return result

    def writeit(filename, content):
        import codecs
        """
        Create a new file with the given content.

        :param str filename:
        :param str content:
        """
        content = content.rstrip('\n') + '\n'
        with codecs.open(filename, 'w', "UTF-8") as oss:
            oss.write(content)

    def generate_file(directory_, filename_, variables_, template='default'):
        """
        Generates a file from a template + variables into the given directory.

        :param str directory_:
        :param str filename_:
        :param dict variables_:
        :param str template:
        """
        template_content = read_template_file(filename_, template)
        content = expandit(template_content, variables_)

        output_filename = os.path.join(directory_, filename_)
        output_filename = expandit(output_filename, variables_)
        writeit(output_filename, content)

    if not directories:
        directories = ('.',)

    directories = [os.path.abspath(i) for i in directories]

    for i_directory in directories:
        Console.title(i_directory)
        try:
            configuration = Anatomy.create_from_directory(i_directory)
        except IOError:
            Console.item('{}: Anatomy configuration file not found.'.format(i_directory))
            continue
        for i_filename in configuration.filenames:
            Console.item(i_filename)
            generate_file(i_directory, i_filename, configuration.variables, configuration.template)
