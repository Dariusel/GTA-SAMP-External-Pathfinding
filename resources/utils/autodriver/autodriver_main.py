import sys, os
import math
from typing import List
from time import sleep
from threading import Thread
from enum import Enum

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from resources.utils.memory.memory_adresses import *
from resources.utils.nodes_classes import PathNode, SlowdownType
from resources.utils.vectors import Vector3
from resources.utils.keypress import key_down, key_up
from resources.utils.math_utils import calculate_look_at_angle, calculate_angle_between_3_positions


class Autodriver():
    _instance = None

    # Configuration
    UPDATE_INTERVAL = 0.04  # Update interval for autodriver in seconds

    # Main
    DISTANCE_TO_NODE_THRESHOLD = 17.5  # Distance threshold to switch to the next node
    ANGLE_DIFFERENCE_THRESHOLD = 6  # Maximum allowable angle difference when turning towards node

    # Speed
    MAX_SPEED = 1.2  # Maximum autodriver speed

    MAX_SLOWDOWN_SPEED = 0.6 # Maximum speed when having to slow down for a turn
    MAX_BRAKING_SPEED = 0.3  # Maximum speed when having to brake/take a turn

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


    def get_slowdown_node(self):
        for i in range(self.current_node_index, len(self.path) - 1):
            # If not first or last element
            if self.path[i] == self.path[0] or self.path[i] == self.path[-1]:
                continue
            
            # Dont get the same node
            if self.path[i] == self.path[self.current_node_index]:
                continue
            
            node_angle_rad = calculate_angle_between_3_positions(self.path[i-1].position,
                                                                     self.path[i].position,
                                                                     self.path[i+1].position)
            node_angle_deg = math.degrees(node_angle_rad)

            # If found slight angle then get sum angle of next ANGLE_DETECTION_COUNT nodes
            if node_angle_deg <= Autodriver.ANGLE_DETECTION_THRESHOLD:
                # Check if there are ANGLE_DETECTION_COUNT nodes in front of this before calculating
                if i >= (len(self.path) - Autodriver.ANGLE_DETECTION_COUNT):
                    continue

                # Get sum of next angles
                cur_angle_detection_sum_deg = 0
                for j in range(i, i + Autodriver.ANGLE_DETECTION_COUNT):
                    cur_node_angle_rad = calculate_angle_between_3_positions(self.path[j-1].position,
                                                                             self.path[j].position,
                                                                             self.path[j+1].position)
                    cur_node_angle_deg = math.degrees(cur_node_angle_rad)

                    cur_angle_detection_sum_deg += 180 - cur_node_angle_deg
                cur_angle_detection_sum_deg = 180 - cur_angle_detection_sum_deg
                print(f'(GNSN) - I: {i}, Angles_Sum_Deg: {cur_angle_detection_sum_deg}')

                if cur_angle_detection_sum_deg <= Autodriver.BRAKE_ANGLE:
                    return self.path[i], SlowdownType.BRAKE
                
                if cur_angle_detection_sum_deg <= Autodriver.SLOWDOWN_ANGLE:
                    return self.path[i], SlowdownType.SLOWDOWN
                
        
        # Return last node in path to brake when finish
        return self.path[-1], SlowdownType.FINISH


    def _drive(self):
        # Find first slowdown_node
        slowdown_node, slowdown_node_type = self.get_slowdown_node()
        print(f'{slowdown_node.node_id} TYPE({slowdown_node_type})')

        # Iterate over each node remaining in self.path
        for i, cur_node in enumerate(self.path, start=self.current_node_index):
            self.current_node_index = i

            driver_pos = Vector3(self.gta_sa.read_float(PLAYER_X),
                                 self.gta_sa.read_float(PLAYER_Y),
                                 self.gta_sa.read_float(PLAYER_Z))
            driver_orientation = self.gta_sa.read_float(PLAYER_ANGLE_RADIANS)

            node_pos = cur_node.position

            driver_to_node_distance = Vector3.distance(driver_pos, node_pos)
        
            # Drive to node while distance is smaller then threshold
            while driver_to_node_distance > Autodriver.DISTANCE_TO_NODE_THRESHOLD:
                if self.is_paused:
                    return

                driver_pos = Vector3(
                    self.gta_sa.read_float(PLAYER_X),
                    self.gta_sa.read_float(PLAYER_Y),
                    self.gta_sa.read_float(PLAYER_Z))
                driver_orientation = self.gta_sa.read_float(PLAYER_ANGLE_RADIANS)

                driver_to_node_angle = calculate_look_at_angle(driver_pos, driver_orientation, node_pos)
                driver_to_node_angle = math.degrees(driver_to_node_angle)

                driver_to_node_distance = Vector3.distance(driver_pos, node_pos)
                driver_to_slowdown_node_distance = Vector3.distance(driver_pos, slowdown_node.position) if slowdown_node else float('inf')
                
                cur_speed = self.gta_sa.read_float(CAR_SPEED)

                # Calculate target_speed
                # Braking Logic
                if slowdown_node_type == SlowdownType.SLOWDOWN:
                    target_speed = max(
                        Autodriver.MAX_SPEED * min(
                            (driver_to_slowdown_node_distance - Autodriver.DISTANCE_TO_NODE_THRESHOLD*1.5) / Autodriver.SLOWDOWN_DISTANCE,
                            1
                        ),
                        Autodriver.MAX_SLOWDOWN_SPEED
                    )

                # Slow-down Logic
                elif slowdown_node_type == SlowdownType.BRAKE:
                    target_speed = max(
                        Autodriver.MAX_SPEED * min(
                            (driver_to_slowdown_node_distance - Autodriver.DISTANCE_TO_NODE_THRESHOLD*1.25) / Autodriver.BRAKING_DISTANCE,
                            1
                        ),
                        Autodriver.MAX_BRAKING_SPEED
                    )

                # Finish Logic
                elif slowdown_node_type == SlowdownType.FINISH:
                    target_speed = Autodriver.MAX_SPEED * min(
                        (driver_to_slowdown_node_distance - Autodriver.DISTANCE_TO_NODE_THRESHOLD*1.5) / Autodriver.FINISH_DISTANCE,
                        1
                    )

                # Throttle Control
                if cur_speed < target_speed:
                    key_down(ord('W'))
                    key_up(ord('S'))
                else:
                    key_up(ord('W'))

                    speed_difference = cur_speed - target_speed
                    if speed_difference > Autodriver.BRAKING_SPEED_DIFFERENCE_THRESHOLD:
                        key_down(ord('S'))

                # Direction Control
                if driver_to_node_angle.__abs__() > Autodriver.ANGLE_DIFFERENCE_THRESHOLD:
                    
                    if driver_to_node_angle > 0:
                        key_down(ord('D'))
                        key_up(ord('A'))
                    else:
                        key_down(ord('A'))
                        key_up(ord('D'))
                else:
                    key_up(ord('D'))
                    key_up(ord('A'))

                sleep(Autodriver.UPDATE_INTERVAL)

            if cur_node == slowdown_node:
                slowdown_node, slowdown_node_type = self.get_slowdown_node()
                print(f'{slowdown_node.node_id} TYPE({slowdown_node_type})')

        key_up(ord('W'))
        key_up(ord('S'))
                    


if __name__ == '__main__':
    #autodriver = Autodriver(None)
    #autodriver.start_driving()
    pass