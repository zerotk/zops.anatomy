def yaml_fom_file(filename_):
    import yaml

    with open(filename_, 'r') as iss:
        content = iss.read()
        result = yaml.load(content)
    return result


def yaml_load(text):
    import yaml
    return yaml.load(text)
