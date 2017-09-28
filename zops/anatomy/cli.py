# -*- coding: utf-8 -*-
import os
from zerotk.zops import Console

import click


ANATOMY_FILENAME = 'anatomy.yml'


click.disable_unicode_literals_warning = True


@click.group('anatomy')
def main():
    pass


@main.command('tree')
@click.pass_context
def tree(ctx):
    from zops.anatomy.layers.feature import AnatomyFeatureRegistry
    _register_features()

    items = AnatomyFeatureRegistry.tree()
    items = sorted([('/' not in filename, filename, fileid, feature) for (feature, fileid, filename) in items])

    column_width = max([len(i[3]) for i in items])
    item_format = '{{:{}}}  {{}}'.format(column_width)

    for _priority, i_filename, i_fileid, i_feature in items:
        Console.item(item_format.format(i_feature, i_filename))


@main.command()
@click.argument('directories', nargs=-1)
@click.pass_context
def apply(ctx, directories):
    """
    Apply templates.
    """
    from .layers.playbook import AnatomyPlaybook

    _register_features()

    if not directories:
        directories = ('.',)
    directories = [os.path.abspath(i) for i in directories]

    for i_directory in directories:
        Console.title(i_directory)
        anatomy_playbook = AnatomyPlaybook.from_file(i_directory + '/anatomy-playbook.yml')
        anatomy_playbook.apply(i_directory)


def _register_features():
    from .layers.feature import AnatomyFeatureRegistry
    filename = os.environ['ZOPS_ANATOMY_FEATURES']
    AnatomyFeatureRegistry.register_from_file(filename)
