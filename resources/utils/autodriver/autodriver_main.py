import sys, os
import win32con, win32api
import math
from typing import List
from time import sleep
from threading import Thread
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from resources.utils.memory.memory_adresses import *
from resources.utils.nodes_classes import PathNode
from resources.utils.vectors import Vector3
from resources.utils.keypress import key_down, key_up
from resources.utils.math_utils import calculate_look_at_angle

class Autodriver():
    _instance = None

    #Config
    distance_to_node_threshold = 20 # From what distance to the current node can autodriver switch to next node
    angle_difference_threshold = 7.5 # How many degrees off can autodriver be when turning towards node
    update_interval = 0.05 # Update interval for autodriver in seconds

    def __init__(self, path: List[PathNode]):
        if Autodriver._instance:
            print("(Autodriver) -> Only one instance allowed.")
            return
        Autodriver._instance = self
        
        self.gta_sa = try_get_gta_sa()
        self.is_paused = False

        if self.gta_sa == None:
            print("(Autodriver) -> 'gta_sa.exe' must be running!")
            return


        self.path = path
        self.current_node_index = 0

    
    def start_driving(self):
        self.is_paused = False

        thread = Thread(target=self._drive, daemon=True)
        thread.start()

    
    def pause_driving(self, bool):
        self.is_paused = bool

        if not self.is_paused:
            self.start_driving()


    def destroy(self):
        Autodriver._instance = None
        self.is_paused = True
        del self


    def _drive(self):
        # Iterate over each node remaining in self.path
        for cur_node in self.path[self.current_node_index:]:
            driver_pos = Vector3(self.gta_sa.read_float(PLAYER_X),
                                 self.gta_sa.read_float(PLAYER_Y),
                                 self.gta_sa.read_float(PLAYER_Z))
            driver_orientation = self.gta_sa.read_float(PLAYER_ANGLE_RADIANS)

            node_pos = cur_node.position

            driver_to_node_distance = Vector3.distance(driver_pos, node_pos)

            # Drive to node while distance is smaller then threshold
            while driver_to_node_distance > Autodriver.distance_to_node_threshold:
                if self.is_paused:
                    return
                
                # Accelerate
                #key_down(ord('W'))

                driver_pos = Vector3(self.gta_sa.read_float(PLAYER_X),
                                 self.gta_sa.read_float(PLAYER_Y),
                                 self.gta_sa.read_float(PLAYER_Z))
                driver_orientation = self.gta_sa.read_float(PLAYER_ANGLE_RADIANS)

                driver_to_node_angle = calculate_look_at_angle(driver_pos, driver_orientation, node_pos)
                driver_to_node_angle = math.degrees(driver_to_node_angle)


                # Turn left/right based on angle
                if driver_to_node_angle.__abs__() > Autodriver.angle_difference_threshold:
                    
                    if driver_to_node_angle > 0:
                        key_down(ord('D'))
                        key_up(ord('A'))
                    else:
                        key_down(ord('A'))
                        key_up(ord('D'))
                # Release turning keys if angle is good
                else:
                    key_up(ord('D'))
                    key_up(ord('A'))
                
                # Update driver_to_node distance
                driver_to_node_distance = Vector3.distance(driver_pos, node_pos)
                print(driver_to_node_distance)

                sleep(Autodriver.update_interval)
        
        key_up(ord('W'))
                    


if __name__ == '__main__':
    #autodriver = Autodriver(None)
    #autodriver.start_driving()
    pass