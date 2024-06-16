from threading import Thread
from time import sleep
from resources.utils.memory.memory_adresses import *


# region Blip Change Event
class BlipChangedEvent():
    def __init__(self) -> None:
        self.subscribers = []

    def add_subscriber(self, subscriber):
        if subscriber not in self.subscribers:
            self.subscribers.append(subscriber)

    def send_event(self, *args, **kwargs):
        for subscriber in self.subscribers:
            subscriber(*args, **kwargs)

blip_changed_event = BlipChangedEvent()


last_blip_x_pos = gta_sa.read_float(GPS_BLIP_X) if gta_sa else None
def check_blip_update(interval_s: float):
    global last_blip_x_pos

    while True:
        if gta_sa:
            # Only check blip_x if changed for performance reasons
            cur_blip_x_pos = gta_sa.read_float(GPS_BLIP_X)
    
            if cur_blip_x_pos != last_blip_x_pos:
                last_blip_x_pos = cur_blip_x_pos
    
                blip_changed_event.send_event()
        
        sleep(interval_s)

check_blip_update_thread = Thread(target=check_blip_update, args=[1], daemon=True)
check_blip_update_thread.start()
# endregion



# region Marker Change Event
class MarkerChangedEvent():
    def __init__(self) -> None:
        self.subscribers = []

    def add_subscriber(self, subscriber):
        if subscriber not in self.subscribers:
            self.subscribers.append(subscriber)

    def send_event(self, *args, **kwargs):
        for subscriber in self.subscribers:
            subscriber(*args, **kwargs)

marker_changed_event = BlipChangedEvent()


last_marker_x_pos = gta_sa.read_float(GPS_MARKER_X) if gta_sa else None
def check_marker_update(interval_s: float):
    global last_marker_x_pos

    while True:
        if gta_sa:
            # Only check blip_x if changed for performance reasons
            cur_marker_x_pos = gta_sa.read_float(GPS_MARKER_X)
    
            if cur_marker_x_pos != last_marker_x_pos:
                last_marker_x_pos = cur_marker_x_pos
    
                marker_changed_event.send_event()
        
        sleep(interval_s)

check_marker_update_thread = Thread(target=check_marker_update, args=[1], daemon=True)
check_marker_update_thread.start()
# endregion