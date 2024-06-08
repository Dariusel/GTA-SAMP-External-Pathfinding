import os
import json

resources_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

DNF_FILE = os.path.join(resources_dir,
                        'data',
                        'nodes_data',
                        'unprocessed',
                        'necessary readable nodes.dnf')

NODES_DATA_JSON = os.path.join(resources_dir,
                               'data',
                               'nodes_data',
                               'nodes_data.json')

NODES_DATA_DETAILED_JSON = os.path.join(resources_dir,
                               'data',
                               'nodes_data',
                               'nodes_data_detailed.json')



def load_json(data_json_path):
    with open(data_json_path, 'r') as file:
        data = json.load(file)

    return data