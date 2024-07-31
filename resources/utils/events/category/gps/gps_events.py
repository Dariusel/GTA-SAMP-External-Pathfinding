import sys, os
from threading import Thread
from time import sleep

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))
from resources.utils.events.event_manager import EventManager, EventType
from resources.utils.memory.memory_adresses import gta_sa
from resources.utils.memory.memory_variables import GameData
from resources.utils import vectors

update_interval = 1

# region Blip Change Event
last_blip_x_pos = GameData.blip_pos.x if gta_sa else None
def check_blip_update():
    global last_blip_x_pos

    while True:
        if gta_sa:
            # Only check blip_x if changed for performance reasons
            cur_blip_x_pos = GameData.blip_pos.x
    
            if cur_blip_x_pos != last_blip_x_pos:
                last_blip_x_pos = cur_blip_x_pos
    
                EventManager.send_event(EventType.BlipChangedEvent)
        
        sleep(update_interval)

Thread(target=check_blip_update, daemon=True).start()
# endregion



# region Marker Change Event
last_marker_x_pos = GameData.marker_pos.x if gta_sa else None
def check_marker_update():
    global last_marker_x_pos

    while True:
        if gta_sa:
            # Only check blip_x if changed for performance reasons
            cur_marker_x_pos = GameData.marker_pos.x
    
            if cur_marker_x_pos != last_marker_x_pos:
                last_marker_x_pos = cur_marker_x_pos
    
                EventManager.send_event(EventType.MarkerChangedEvent)
        
        sleep(update_interval)

Thread(target=check_marker_update, daemon=True).start()
# endregion