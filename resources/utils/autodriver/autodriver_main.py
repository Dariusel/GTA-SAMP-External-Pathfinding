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
from resources.utils.math_utils import calculate_look_at_angle, calculate_angle_between_3_positions

class Autodriver():
    _instance = None

    #Config
    update_interval = 0.04 # Update interval for autodriver in seconds

    distance_to_node_threshold = 15 # From what distance to the current node can autodriver switch to next node
    angle_difference_threshold = 7.5 #7.5 How many degrees off can autodriver be when turning towards node

    max_speed = 0.8 # 1.2 for max car speeds
    min_speed = 0

    slow_down_angle = 165 # Node angle where you should slow down

    turn_min_angle = 130 #(110); Minimum angle thats considered a turn
    slowdown_distance_from_turn = 70 # How far from the turn should the car start braking gradually
    braking_distance_from_turn = 17.5 # How far from the turn should the car start full braking
    max_turning_speed = 0.35 # 'CAR_SPEED' variable max number when turning

    braking_speed_difference_threshold = 0.175 # If speed difference between cur_speed and target_speed is more than this brake otherwise release throttle

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


    def get_next_turn_node(self):
        for i in range(self.current_node_index, len(self.path) - 1):
            if self.path[i] != self.path[0] and self.path[i] != self.path[-1]:
                if self.path[i] == self.path[self.current_node_index]:
                    continue
                cur_node_angle_rad = calculate_angle_between_3_positions(self.path[i-1].position,
                                                                         self.path[i].position,
                                                                         self.path[i+1].position)
                cur_node_angle_deg = math.degrees(cur_node_angle_rad)
                # If found turn
                if cur_node_angle_deg <= Autodriver.turn_min_angle:
                    return self.path[i]
        
        # Return last node in path to brake when finish
        return self.path[-1]


    def _drive(self):
        # Find first turn_node
        turn_node = self.get_next_turn_node()

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
            while driver_to_node_distance > Autodriver.distance_to_node_threshold:
                if self.is_paused:
                    return

                driver_pos = Vector3(self.gta_sa.read_float(PLAYER_X),
                                 self.gta_sa.read_float(PLAYER_Y),
                                 self.gta_sa.read_float(PLAYER_Z))
                driver_orientation = self.gta_sa.read_float(PLAYER_ANGLE_RADIANS)

                driver_to_node_angle = calculate_look_at_angle(driver_pos, driver_orientation, node_pos)
                driver_to_node_angle = math.degrees(driver_to_node_angle)

                driver_to_turn_node_distance = Vector3.distance(driver_pos, turn_node.position) if turn_node else float('inf')
                
                cur_speed = self.gta_sa.read_float(CAR_SPEED)

                # Calculate target_speed
                target_speed = Autodriver.max_speed * min(driver_to_turn_node_distance/(Autodriver.slowdown_distance_from_turn+Autodriver.distance_to_node_threshold),
                                                          1)
                if driver_to_turn_node_distance <= Autodriver.braking_distance_from_turn+Autodriver.distance_to_node_threshold:
                    target_speed = Autodriver.max_turning_speed

                # Throttle
                #print(f'Cur({cur_speed}) - Target({target_speed})')
                if cur_speed < target_speed:
                    key_down(ord('W'))
                    key_up(ord('S'))
                else:
                    key_up(ord('W'))

                    speed_difference = cur_speed - target_speed
                    if speed_difference > Autodriver.braking_speed_difference_threshold:
                        key_down(ord('S'))


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

                sleep(Autodriver.update_interval)

            if cur_node == turn_node:
                turn_node = self.get_next_turn_node()
        key_up(ord('W'))
                    


if __name__ == '__main__':
    #autodriver = Autodriver(None)
    #autodriver.start_driving()
    pass