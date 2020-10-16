import os
from os.path import dirname
from zerotk.zops import Console

import click


click.disable_unicode_literals_warning = True


@click.group('anatomy')
def main():
    pass


@main.command('tree')
@click.option('--features-file', default=None, envvar="ZOPS_ANATOMY_FEATURES")
@click.pass_context
def tree(ctx, features_file):
    from zops.anatomy.layers.feature import AnatomyFeatureRegistry

    _register_features(features_file)

    items = AnatomyFeatureRegistry.tree()
    items = sorted([
        ('/' not in filename, filename, fileid, feature)
        for (feature, fileid, filename) in items
    ])

    column_width = max([len(i[3]) for i in items])
    item_format = '{{:{}}}  {{}}'.format(column_width)

    for _priority, i_filename, i_fileid, i_feature in items:
        Console.item(item_format.format(i_feature, i_filename))


@main.command()
@click.argument('directory')
@click.option('--features-file', default=None, envvar="ZOPS_ANATOMY_FEATURES")
@click.option('--playbook-file', default=None)
@click.option('--recursive', '-r', is_flag=True)
@click.pass_context
def apply(ctx, directory, features_file, playbook_file, recursive):
    """
    Apply templates.
    """
    from .layers.playbook import AnatomyPlaybook

    if playbook_file is not None:
        playbook_filenames = [playbook_file]
    elif recursive:
        directory = os.path.abspath(directory)
        playbook_filenames = find_all('anatomy-playbook.yml', directory)
        playbook_filenames = GitIgnored().filter(playbook_filenames)
    else:
        playbook_filenames = [directory + '/anatomy-playbook.yml']

    for i_filename in playbook_filenames:
        features_file = features_file or _find_features_file(dirname(i_filename))

        _register_features(features_file)

        Console.title(directory)
        anatomy_playbook = AnatomyPlaybook.from_file(i_filename)
        anatomy_playbook.apply(directory)


def _find_features_file(path):
    from zerotk.lib.path import find_up

    SEARCH_FILENAMES = [
        'anatomy-features/anatomy-features.yml',
        'anatomy-features.yml',
    ]

    for i_filename in SEARCH_FILENAMES:
        result = find_up(i_filename, path)
        if result is not None:
            break

    if result is None:
        Console.error("Can't find features file: anatomy-features.yml.")
        raise SystemError(1)

    Console.info("Features filename:", result)
    return result


def _register_features(filename):
    from .layers.feature import AnatomyFeatureRegistry

    AnatomyFeatureRegistry.register_from_file(filename)
