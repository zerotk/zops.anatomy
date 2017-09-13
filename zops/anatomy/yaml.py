

def yaml_from_file(filename_):
    with open(filename_, 'r') as iss:
        content = iss.read()
        result = yaml_load(content)
    return result


def yaml_load(text):
    from ruamel.yaml import YAML
    from ruamel.yaml import SafeConstructor
    from collections import OrderedDict

    class OrderedConstructor(SafeConstructor):

        MappingType = OrderedDict

    loader = YAML(typ='safe')
    loader.Constructor = OrderedConstructor
    return loader.load(text)
