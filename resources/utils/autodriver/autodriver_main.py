import sys, os
import win32con, win32api
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
    distance_to_node_threshold = 5

    def __init__(self, path: List[PathNode]):
        if Autodriver._instance:
            print("(Autodriver) -> Only one instance allowed.")
            return
        Autodriver._instance = self
        

        self.gta_sa = try_get_gta_sa()

        if self.gta_sa == None:
            print("(Autodriver) -> 'gta_sa.exe' must be running!")
            return


        self.path = path
        self.current_node_index = 0

    
    def start_driving(self):
        thread = Thread(target=self._start_driving, daemon=True)
        thread.start()
        thread.join()


    def _start_driving(self):
        for cur_node in self.path:
            driver_pos = Vector3(self.gta_sa.read_float(PLAYER_X),
                                 self.gta_sa.read_float(PLAYER_Y),
                                 self.gta_sa.read_float(PLAYER_Z))
            driver_orientation = self.gta_sa.read_float(PLAYER_ANGLE_RADIANS)

            node_pos = cur_node.position


            driver_to_node_distance = Vector3.distance(driver_pos, node_pos)


            while driver_to_node_distance > self.distance_to_node_threshold:
                driver_node_angle = calculate_look_at_angle(driver_pos)
        


if __name__ == '__main__':
    #autodriver = Autodriver(None)
    #autodriver.start_driving()
    pass