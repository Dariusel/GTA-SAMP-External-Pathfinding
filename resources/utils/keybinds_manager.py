from pynput.keyboard import Key, Listener

from resources.gui.gui_main import MainGUI
from resources.gui.nodes_editor.nodes_editor import NodesEditor

# Keybinds
START_AUTODRIVER = frozenset([Key.ctrl_l, Key.alt_l, 'R']) # 'r' from run
PAUSE_AUTODRIVER = frozenset([Key.ctrl_l, Key.alt, 'P'])
STOP_AUTODRIVER = frozenset([Key.ctrl_l, Key.alt_l, 'Q']) # 'q' from quit

GOTO_BLIP = frozenset([Key.ctrl_l, Key.alt_l, 'B'])
GOTO_MARKER = frozenset([Key.ctrl_l, Key.alt_l, 'M'])

NODES_EDITOR_NODE_AT_POSITION = frozenset([Key.ctrl_l, 'N'])


# Functionality
def start_autodriver():
    MainGUI._instance.drive_path()


def pause_autodriver():
    MainGUI._instance.pause_autodriver()


def stop_autodriver():
    MainGUI._instance.stop_autodriver()


def goto_blip():
    MainGUI._instance.drive_to_blip()


def goto_marker():
    MainGUI._instance.drive_to_marker()

def nodes_editor_node_at_position():
    if NodesEditor._instance:
        if hasattr(NodesEditor._instance, 'loaded_window'):
            if NodesEditor._instance.loaded_window:
               NodesEditor._instance.node_at_player_pos()



# Functions Map
hotkey_function_map = {
    START_AUTODRIVER: start_autodriver,
    PAUSE_AUTODRIVER: pause_autodriver,
    STOP_AUTODRIVER: stop_autodriver,
    GOTO_BLIP: goto_blip,
    GOTO_MARKER: goto_marker,
    NODES_EDITOR_NODE_AT_POSITION: nodes_editor_node_at_position,
}


pressed_vks = set()

def get_vk(key):
    if type(key) == str:
        return ord(key)
    else:
        return key.vk if hasattr(key, 'vk') else key.value.vk

def on_press(key):
    # Add pressed key to the set
    vk = get_vk(key)
    pressed_vks.add(vk)
    
    for hotkey, function in hotkey_function_map.items():
        if all(get_vk(k) in pressed_vks for k in hotkey):
            pressed_vks.clear()
            function()
            return

def on_release(key):
    vk = get_vk(key)
    if vk in pressed_vks:
        pressed_vks.remove(vk)
    return


# Keybinds Listener
Listener(on_press=on_press, on_release=on_release).start()


def key_to_str(key):
    if isinstance(key, Key):
        return key.name.upper()
    else:
        return str(key)