import sys, os
import math
from typing import List
from time import sleep
from threading import Thread

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from resources.utils.memory.memory_adresses import *
from resources.utils.nodes_classes import PathNode
from resources.utils.vectors import Vector3
from resources.utils.keypress import key_down, key_up, release_keys
from resources.utils.math_utils import calculate_look_at_angle


class Autodriver():
    _instance = None

    # Configuration
    UPDATE_INTERVAL = 0.04  # Update interval for autodriver in seconds

    # Main
    DISTANCE_TO_NODE_THRESHOLD = 17.5  # Distance threshold to switch to the next node
    ANGLE_DIFFERENCE_THRESHOLD = 6  # Maximum allowable angle difference when turning towards node

    # Speed
    MAX_SPEED = 1.2  # Maximum autodriver speed

    MAX_SLOWDOWN_SPEED = 0.7 # Maximum speed when having to slow down for a turn
    MAX_BRAKING_SPEED = 0.35  # Maximum speed when having to brake/take a turn

    # Braking
    SLOWDOWN_DISTANCE = 75 # Distance from the slowdown node to start braking
    BRAKING_DISTANCE = 75  # Distance from the turn to start braking
    FINISH_DISTANCE = 45 # Distance from the finish node to start braking

    BRAKING_SPEED_DIFFERENCE_THRESHOLD = 0.175  # Speed difference threshold for braking

    # Slowdown Detection
    ANGLE_DETECTION_THRESHOLD = 175 # If a slight angle is detected (<ANGLE_DETECTION_THRESHOLD) check real angle by getting the sum of the next ANGLE_DETECTION_COUNT nodes angles
    ANGLE_DETECTION_COUNT = 5 # If found a slight angle, get the sum of the next ANGLE_DETECTION_COUNT nodes angles

    SLOWDOWN_ANGLE = 145  # Node angle where the car should slow down
    BRAKE_ANGLE = 117.5  # Minimum angle considered a turn

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

    
    def pause_driving(self, bool: bool):
        self.is_paused = bool

        if not self.is_paused:
            self.start_driving()


    def destroy(self):
        Autodriver._instance = None
        self.is_paused = True
        del self


    def _drive(self):
        from resources.utils.autodriver.utils.autodriver_utils import calculate_target_speed, get_slowdown_node, get_navi_node, throttle_control, direction_control
        # Find first slowdown_node
        slowdown_node, slowdown_node_type = get_slowdown_node(self.current_node_index, self.path)
        #print(f'{slowdown_node.node_id} TYPE({slowdown_node_type})')

        # Iterate over each node remaining in self.path
        for i, cur_node in enumerate(self.path, start=self.current_node_index):
            self.current_node_index = i
    
            driver_pos = Vector3(self.gta_sa.read_float(PLAYER_X),
                                 self.gta_sa.read_float(PLAYER_Y),
                                 self.gta_sa.read_float(PLAYER_Z))
            driver_orientation = self.gta_sa.read_float(PLAYER_ANGLE_RADIANS)

            driver_to_node_distance = Vector3.distance(driver_pos, cur_node.position)
        
            # Drive to node while distance is smaller then threshold
            while driver_to_node_distance > Autodriver.DISTANCE_TO_NODE_THRESHOLD:
                if self.is_paused:
                    return

                driver_pos = Vector3(
                    self.gta_sa.read_float(PLAYER_X),
                    self.gta_sa.read_float(PLAYER_Y),
                    self.gta_sa.read_float(PLAYER_Z))
                driver_orientation = self.gta_sa.read_float(PLAYER_ANGLE_RADIANS)

                driver_to_node_angle = calculate_look_at_angle(driver_pos, driver_orientation, cur_node.position)
                driver_to_node_angle = math.degrees(driver_to_node_angle)

                driver_to_node_distance = Vector3.distance(driver_pos, cur_node.position)
                driver_to_slowdown_node_distance = Vector3.distance(driver_pos, slowdown_node.position) if slowdown_node else float('inf')

                cur_navi = get_navi_node(self.current_node_index, self.path)
                
                cur_speed = self.gta_sa.read_float(CAR_SPEED)

                # Calculate target_speed
                target_speed = calculate_target_speed(cur_speed, driver_to_slowdown_node_distance, slowdown_node_type)

                # Throttle Control
                throttle_control(cur_speed, target_speed)

                # Direction Control
                direction_control(driver_to_node_angle)

                sleep(Autodriver.UPDATE_INTERVAL)

            if cur_node == slowdown_node:
                slowdown_node, slowdown_node_type = get_slowdown_node(self.current_node_index, self.path)
                #print(f'{slowdown_node.node_id} TYPE({slowdown_node_type})')

        release_keys()
                    


if __name__ == '__main__':
    #autodriver = Autodriver(None)
    #autodriver.start_driving()
    pass