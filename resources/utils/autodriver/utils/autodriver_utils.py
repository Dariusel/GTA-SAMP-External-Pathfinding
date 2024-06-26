import math
from typing import List

from resources.utils.keypress import key_down, key_up
from resources.utils.autodriver.autodriver_main import Autodriver
from resources.utils.nodes_classes import PathNode, SlowdownType
from resources.utils.math_utils import calculate_angle_between_2_vectors
from resources.utils.vectors import Vector2


def calculate_target_speed(cur_speed: float, driver_to_slowdown_node_distance: float, slowdown_node_type: SlowdownType):
        # Braking Logic
        cur_speed_normalized = cur_speed / Autodriver.MAX_SPEED
        if slowdown_node_type == SlowdownType.SLOWDOWN:
            return max(
                Autodriver.MAX_SPEED * min(
                    (driver_to_slowdown_node_distance - Autodriver.DISTANCE_TO_NODE_THRESHOLD*cur_speed_normalized) / Autodriver.SLOWDOWN_DISTANCE,
                    1
                ),
                Autodriver.MAX_SLOWDOWN_SPEED
            )
        # Slow-down Logic
        elif slowdown_node_type == SlowdownType.BRAKE:
            return max(
                Autodriver.MAX_SPEED * min(
                    (driver_to_slowdown_node_distance - Autodriver.DISTANCE_TO_NODE_THRESHOLD*cur_speed_normalized) / Autodriver.BRAKING_DISTANCE,
                    1
                ),
                Autodriver.MAX_BRAKING_SPEED
            )
        # Finish Logic
        elif slowdown_node_type == SlowdownType.FINISH:
            return Autodriver.MAX_SPEED * min(
                driver_to_slowdown_node_distance / Autodriver.FINISH_DISTANCE,
                1
            )
        

def get_slowdown_node(current_node_index, path):
        for i in range(current_node_index, len(path) - 1):
            # If not first or last element
            if path[i] == path[0] or path[i] == path[-1]:
                continue
            
            # Dont get the same node
            if path[i] == path[current_node_index]:
                continue
            
            ba_vector = Vector2(path[i-1].position.x - path[i].position.x, path[i-1].position.z - path[i].position.z)
            bc_vector = Vector2(path[i+1].position.x - path[i].position.x, path[i+1].position.z - path[i].position.z)
            node_angle_rad = calculate_angle_between_2_vectors(ba_vector, bc_vector)
            node_angle_deg = math.degrees(node_angle_rad)

            # If found slight angle then get sum angle of next ANGLE_DETECTION_COUNT nodes
            if node_angle_deg <= Autodriver.ANGLE_DETECTION_THRESHOLD:
                # Check if there are ANGLE_DETECTION_COUNT nodes in front of this before calculating
                if i >= (len(path) - Autodriver.ANGLE_DETECTION_COUNT):
                    continue

                # Get sum of next angles
                cur_angle_detection_sum_deg = 0
                for j in range(i, i + Autodriver.ANGLE_DETECTION_COUNT):
                    ba_vector = Vector2(path[j-1].position.x - path[j].position.x, path[j-1].position.z - path[j].position.z)
                    bc_vector = Vector2(path[j+1].position.x - path[j].position.x, path[j+1].position.z - path[j].position.z)
                    cur_node_angle_rad = calculate_angle_between_2_vectors(ba_vector, bc_vector)
                    cur_node_angle_deg = math.degrees(cur_node_angle_rad)

                    cur_angle_detection_sum_deg += 180 - cur_node_angle_deg
                cur_angle_detection_sum_deg = 180 - cur_angle_detection_sum_deg
                #print(f'(GNSN) - I: {i}, Angles_Sum_Deg: {cur_angle_detection_sum_deg}')

                if cur_angle_detection_sum_deg <= Autodriver.BRAKE_ANGLE:
                    return path[i], SlowdownType.BRAKE
                
                if cur_angle_detection_sum_deg <= Autodriver.SLOWDOWN_ANGLE:
                    return path[i], SlowdownType.SLOWDOWN
                
        
        # Return last node in path to brake when finish
        return path[-1], SlowdownType.FINISH


def get_navi_node(current_node_index, path: List[PathNode]):
        cur_navi = None
        if current_node_index < len(path)-1:
            next_node_id = path[current_node_index+1].node_id
            for adj_node in path[current_node_index].adj_nodes.values():
                if adj_node['node_id'] == next_node_id:
                    cur_navi = adj_node['navi']
                    return cur_navi
                

def throttle_control(cur_speed: float, target_speed: float):
    if cur_speed < target_speed:
        key_down(ord('W'))
        key_up(ord('S'))
    else:
        key_up(ord('W'))
        speed_difference = cur_speed - target_speed
        if speed_difference > Autodriver.BRAKING_SPEED_DIFFERENCE_THRESHOLD:
            key_down(ord('S'))


def direction_control(driver_to_node_angle: float):
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