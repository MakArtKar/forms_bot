import yaml

def load_yml_file(filename: str):
    with open(filename) as fin:
        text_data = fin.read()
    # https://github.com/yaml/pyyaml/wiki/PyYAML-yaml.load(input)-Deprecation
    return yaml.unsafe_load(text_data)
