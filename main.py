﻿import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'resources')))
import resources.utils.keybinds_manager
from resources.utils.math_utils import calculate_angle_between_3_positions
from resources.utils.vectors import Vector3
from resources.utils.json_utils import load_json, save_json
from resources.utils.file_paths import NODES_DATA_JSON
from resources.utils.pathfinding.Dijkstra import pathfind_dijkstra
from resources.utils.nodes_classes import PathNode
from resources.gui.gui_main import MainGUI
from resources.utils.memory.memory_adresses import *
from resources.utils.memory.utils.memory_utils import *
from resources.utils.autodriver.autodriver_main import *


if __name__ == '__main__':
    #p1 = Vector3(4,0,0)
    #p2 = Vector3(0,0,0)
    #p3 = Vector3(2,0,2)

    #print(calculate_angle_between_3_positions(p1,p2,p3))
    # Start the gui
    gui = MainGUI()
    
    gui.display_main()
    