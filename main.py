from resources.utils.json_utils import load_json, save_json
from resources.utils.pathfinding.Dijkstra import pathfind_dijkstra
from resources.utils.nodes_classes import PathNode
from resources.gui.gui_main import MainGUI


if __name__ == '__main__':
    # Start the gui
    gui = MainGUI()

    gui.display_main()
    