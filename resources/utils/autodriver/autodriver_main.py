import sys, os
import math
from typing import List
from time import sleep
from threading import Thread
import configparser

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from copy import copy
from resources.utils.memory.memory_adresses import *
from resources.utils.nodes_classes import PathNode, SlowdownType
from resources.utils.vectors import Vector3
from resources.utils.keypress import key_down, key_up, release_keys
from resources.utils.math_utils import calculate_look_at_angle, angle_to_vector


class Autodriver():
    _instance = None
    _config_file = None

    def __init__(self, path: List[PathNode]):
        if Autodriver._instance:
            print("(Autodriver) -> Only one instance allowed.")
            return
        Autodriver._instance = self
        
        self.gta_sa = try_get_gta_sa()
        self.is_paused = False

        self.is_circuit = False

        if self.gta_sa == None:
            print("(Autodriver) -> 'gta_sa.exe' must be running!")
            return


        self.path = path
        self.current_node_index = 0

        # region Configuration
        self.config_file = configparser.ConfigParser()
        self.config_file.read(Autodriver._config_file)

        self.UPDATE_INTERVAL = float(self.config_file.get('AutodriverConfig', 'UPDATE_INTERVAL'))  # Update interval for autodriver in seconds

        # Main
        self.DISTANCE_TO_NODE_THRESHOLD = float(self.config_file.get('AutodriverConfig', 'DISTANCE_TO_NODE_THRESHOLD'))  # Distance threshold to switch to the next node
        self.ANGLE_DIFFERENCE_THRESHOLD = float(self.config_file.get('AutodriverConfig', 'ANGLE_DIFFERENCE_THRESHOLD'))  # Maximum allowable angle difference when turning towards node

        # Speed
        self.MAX_SPEED = float(self.config_file.get('AutodriverConfig', 'MAX_SPEED'))  # Maximum autodriver speed

        self.MAX_SLOWDOWN_SPEED = float(self.config_file.get('AutodriverConfig', 'MAX_SLOWDOWN_SPEED')) # Maximum speed when having to slow down for a turn
        self.MAX_BRAKING_SPEED = float(self.config_file.get('AutodriverConfig', 'MAX_BRAKING_SPEED'))  # Maximum speed when having to brake/take a turn
        self.MAX_FINISH_SPEED = float(self.config_file.get('AutodriverConfig', 'MAX_FINISH_SPEED')) # Max speed when coming to a stop for finishing

        # Braking
        self.SLOWDOWN_DISTANCE = float(self.config_file.get('AutodriverConfig', 'SLOWDOWN_DISTANCE')) # Distance from the slowdown node to start braking
        self.BRAKING_DISTANCE = float(self.config_file.get('AutodriverConfig', 'BRAKING_DISTANCE'))  # Distance from the turn to start braking
        self.FINISH_DISTANCE = float(self.config_file.get('AutodriverConfig', 'FINISH_DISTANCE')) # Distance from the finish node to start braking

        self.BRAKING_SPEED_DIFFERENCE_THRESHOLD = float(self.config_file.get('AutodriverConfig', 'BRAKING_SPEED_DIFFERENCE_THRESHOLD'))  # Speed difference threshold for braking

        # Slowdown Detection
        self.ANGLE_DETECTION_THRESHOLD = float(self.config_file.get('AutodriverConfig', 'ANGLE_DETECTION_THRESHOLD')) # If a slight angle is detected (<ANGLE_DETECTION_THRESHOLD) check real angle by getting the sum of the next ANGLE_DETECTION_COUNT nodes angles
        self.ANGLE_DETECTION_COUNT = int(self.config_file.get('AutodriverConfig', 'ANGLE_DETECTION_COUNT')) # If found a slight angle, get the sum of the next ANGLE_DETECTION_COUNT nodes angles

        self.SLOWDOWN_ANGLE = float(self.config_file.get('AutodriverConfig', 'SLOWDOWN_ANGLE'))  # Node angle where the car should slow down
        self.BRAKE_ANGLE = float(self.config_file.get('AutodriverConfig', 'BRAKE_ANGLE'))  # Minimum angle considered a turn
        #endregion

    
    def start_driving(self, is_circuit: bool=False):
        self.is_paused = False
        self.is_circuit = is_circuit

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
        from resources.utils.autodriver.utils.autodriver_utils import (
            calculate_target_speed, get_slowdown_node, get_navi_node_and_vector,
            throttle_control, direction_control, get_lane_offset_based_on_navi,
            apply_lane_offset_to_node, update_autodriver_instance, driver
        )
        update_autodriver_instance()

        # Find the first slowdown node
        slowdown_node, slowdown_node_type = get_slowdown_node(self.current_node_index, self.path, self.is_circuit)

        # Iterate over each node remaining in self.path
        for i, cur_node in enumerate(self.path[self.current_node_index:], start=self.current_node_index):
            self.current_node_index = i            

            # Create a copy of cur_node to avoid modifying the original path
            target_node = copy(cur_node)

            # Read the current driver position and orientation
            driver_pos = Vector3(self.gta_sa.read_float(PLAYER_X),
                                 self.gta_sa.read_float(PLAYER_Y),
                                 self.gta_sa.read_float(PLAYER_Z))
            driver_orientation = self.gta_sa.read_float(PLAYER_ANGLE_RADIANS)

            # Lane detection system
            #cur_navi, target_node_direction_vector = get_navi_node_and_vector(self.current_node_index, self.path)
            #if cur_navi and target_node_direction_vector:
            #    lane_offset = get_lane_offset_based_on_navi(cur_navi, target_node_direction_vector, 1)
            #    target_node = apply_lane_offset_to_node(target_node, cur_navi.direction, lane_offset)

            # Calculate the distance to the target node
            driver_to_node_distance = Vector3.distance(driver_pos, target_node.position)
        
            # Drive to the target node while the distance is greater than the threshold
            while driver_to_node_distance > self.DISTANCE_TO_NODE_THRESHOLD:
                if self.is_paused:
                    return

                # Update the driver position and orientation
                driver_pos = Vector3(
                    self.gta_sa.read_float(PLAYER_X),
                    self.gta_sa.read_float(PLAYER_Y),
                    self.gta_sa.read_float(PLAYER_Z))
                driver_orientation = self.gta_sa.read_float(PLAYER_ANGLE_RADIANS)

                # Calculate the angle and distance to the target node
                driver_to_node_angle = calculate_look_at_angle(driver_pos, driver_orientation, target_node.position)
                driver_to_node_angle = math.degrees(driver_to_node_angle)
                driver_to_node_distance = Vector3.distance(driver_pos, target_node.position)

                # Calculate the distance to the slowdown node
                driver_to_slowdown_node_distance = Vector3.distance(driver_pos, slowdown_node.position) if slowdown_node else float('inf')
                
                # Read the current speed of the car
                cur_speed = self.gta_sa.read_float(CAR_SPEED)

                # Calculate the target speed
                target_speed = calculate_target_speed(cur_speed, driver_to_slowdown_node_distance, slowdown_node_type, driver_to_node_angle)
                print(f'Targ: {round(target_speed, 2)} | Dist: {round(driver_to_slowdown_node_distance, 2)}, Angle: {round(driver_to_node_angle, 2)} | Type: {slowdown_node_type}')

                # Control the throttle and direction
                throttle_control(cur_speed, target_speed)
                direction_control(driver_to_node_angle)

                # Pause for the update interval
                sleep(self.UPDATE_INTERVAL)

            # Update the slowdown node if the current node is the slowdown node
            if cur_node == slowdown_node:
                slowdown_node, slowdown_node_type = get_slowdown_node(self.current_node_index, self.path, self.is_circuit)

        # Release control keys after the path is completed
        release_keys()
        
        # If it's a circuit, restart the drive from the beginning
        if self.is_circuit:
            self.current_node_index = 0
            self._drive()
                    


if __name__ == '__main__':
    #autodriver = Autodriver(None)
    #autodriver.start_driving()
    pass