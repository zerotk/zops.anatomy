# -*- coding: utf-8 -*-
import os
from zerotk.zops import Console

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
    Apply templates.
    """
    from .engine import AnatomyFeatureRegistry
    from .playbook import AnatomyPlaybook

    AnatomyFeatureRegistry.register_from_file(
        '/home/kaniabi/Projects/zerotk/zops.anatomy/templates/anatomy-features.yml'
    )

    if not directories:
        directories = ('.',)
    directories = [os.path.abspath(i) for i in directories]

    for i_directory in directories:
        Console.title(i_directory)
        anatomy_playbook = AnatomyPlaybook.from_file(i_directory + '/anatomy-playbook.yml')
        anatomy_playbook.apply(i_directory)
