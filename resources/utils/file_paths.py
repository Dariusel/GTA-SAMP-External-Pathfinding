import sys, os

resources_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

MAP_IMG_PATH = os.path.join(resources_dir,
                        'data',
                        'map',
                        'map.png')

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

SOLVED_PATH_NODES_DATA = os.path.join(resources_dir,
                               'data',
                               'nodes_data',
                               'debug',
                               'solved_path_1.json')