def read_yaml(filename_):
    import yaml

    with open(filename_, 'r') as iss:
        content = iss.read()
        result = yaml.load(content)
    return result
