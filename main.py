import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'resources')))
from resources.utils.json_utils import load_json, save_json
from resources.utils.file_paths import NODES_DATA_JSON
from resources.utils.pathfinding.Dijkstra import pathfind_dijkstra
from resources.utils.nodes_classes import PathNode
from resources.gui.gui_main import MainGUI
from resources.utils.memory.memory_adresses import *
from resources.utils.autodriver.autodriver_main import *


if __name__ == '__main__':
    # Start the gui
    gui = MainGUI()
    
    gui.display_main()
    