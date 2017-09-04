import yaml
import yamlordereddictloader


def yaml_fom_file(filename_):
    with open(filename_, 'r') as iss:
        content = iss.read()
        result = yaml.load(
            content,
            Loader=yamlordereddictloader.Loader
        )
    return result


def yaml_load(text):
    return yaml.load(text)
