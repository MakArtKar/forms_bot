import yaml

def load_yml_file(filename: str):
    with open(filename) as fin:
        text_data = fin.read()
    return yaml.load(text_data) 