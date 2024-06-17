from pynput import keyboard
from threading import Thread

from resources.gui.gui_main import MainGUI


# Keybinds
START_AUTODRIVER = '<ctrl>+<alt>+r' # 'r' from run
STOP_AUTODRIVER = '<ctrl>+<alt>+s' # 's' from stop



# Functionality
def start_autodriver():
    pass


def stop_autodriver():
    MainGUI._instance.stop_autodriver()


# Applying keybinds
def keybinds_listener():
    with keyboard.GlobalHotKeys({
            START_AUTODRIVER: start_autodriver,
            STOP_AUTODRIVER: stop_autodriver}) as h:
         h.join()

keybinds_listener_thread = Thread(target=keybinds_listener, daemon=True)
keybinds_listener_thread.start()