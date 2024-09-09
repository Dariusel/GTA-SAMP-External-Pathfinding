import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'resources')))
import resources.utils.keybinds_manager # IMPORTANT - DO NOT REMOVE
from resources.gui.gui_main import MainGUI
from resources.utils.memory.memory_adresses import *
from resources.utils.memory.utils.memory_utils import *
from resources.utils.autodriver.autodriver_main import *


if __name__ == '__main__':
    # Start the gui
    gui = MainGUI()
    
    gui.display_main()
    