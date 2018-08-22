import json
import sys, getopt, os

## Commons I/O
def makedir(path):
    if not path or os.path.exists(path):
        return []
    (head, tail) = os.path.split(path)
    res = makedir(head)
    if not os.path.exists(path):
        os.mkdir(path)
    res += [path]
    return res


def load_json_file(json_file: str) -> object:
    """ Loads a json file into a dictionary
    :rtype: dict
    """
    with open(json_file) as data_file:
        data = json.load(data_file)
    return data


def save_json_path_file(path: str, filename: str, data: dict):
    """ Write a dictionary as a json file """
    makedir(path)
    if not path.endswith('/'):
        path += '/'
    print('saving Json file: ', filename, ' in path: ', path)
    with open(path + filename, 'w') as outfile:
        json.dump(data, outfile, indent=2)


def save_json_file(pathfile: str, data: dict):
    """ Write a dictionary as a json file """
    path, filename = os.path.split(pathfile)
    save_json_path_file(path, filename, data)