import keyboard
from threading import Thread

from resources.gui.gui_main import MainGUI


# Keybinds
START_AUTODRIVER = 'ctrl+alt+r' # 'r' from run
STOP_AUTODRIVER = 'ctrl+alt+g' # 's' from stop


# Functionality
def start_autodriver():
    pass


def stop_autodriver():
    print('stopped')
    MainGUI._instance.stop_autodriver()


# Applying keybinds
keyboard.add_hotkey(START_AUTODRIVER, start_autodriver)
keyboard.add_hotkey(STOP_AUTODRIVER, stop_autodriver)