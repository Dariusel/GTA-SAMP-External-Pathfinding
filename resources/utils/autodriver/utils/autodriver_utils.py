import math
from typing import List

from resources.utils.keypress import key_down, key_up
from resources.utils.autodriver.autodriver_main import Autodriver
from resources.utils.nodes_classes import PathNode, SlowdownType, Navi
from resources.utils.math_utils import calculate_angle_between_2_vectors, vector_to_angle
from resources.utils.vectors import Vector2, Vector3
from resources.utils.binary_utils import flags_data_extractor

driver = Autodriver._instance

def update_autodriver_instance():
    global driver
    driver = Autodriver._instance


def calculate_target_speed(cur_speed: float, driver_to_slowdown_node_distance: float, slowdown_node_type: SlowdownType, driver_to_node_angle: float):
        driver_to_node_angle = driver_to_node_angle.__abs__()

        driver_to_node_angle_multiplier = 1
        if driver_to_node_angle > driver.ANGLE_DIFFERENCE_THRESHOLD:
            driver_to_node_angle_multiplier = max(1 - (driver_to_node_angle / 55), 0.1) # Remap from [0,90] to [0,1] and inverse it so its [1,0]

        # Braking Logic
        cur_speed_normalized = cur_speed / driver.MAX_SPEED # Second part only tweaks it so it brakes later
        if slowdown_node_type == SlowdownType.SLOWDOWN:
            return max(
                 driver_to_node_angle_multiplier * max(
                    driver.MAX_SPEED * min(
                        driver_to_slowdown_node_distance / driver.SLOWDOWN_DISTANCE*cur_speed_normalized,
                        1
                    ),
                    driver.MAX_SLOWDOWN_SPEED
                ),
                driver.MAX_BRAKING_SPEED
            )
        # Slow-down Logic
        elif slowdown_node_type == SlowdownType.BRAKE:
            return max(
                driver.MAX_SPEED * driver_to_node_angle_multiplier * min(
                    driver_to_slowdown_node_distance / driver.BRAKING_DISTANCE*cur_speed_normalized,
                    1
                ),
                driver.MAX_BRAKING_SPEED
            )
        # Finish Logic
        elif slowdown_node_type == SlowdownType.FINISH:
            return max(
                driver.MAX_SPEED * driver_to_node_angle_multiplier * min(
                    (driver_to_slowdown_node_distance-driver.DISTANCE_TO_NODE_THRESHOLD*1.5) / driver.FINISH_DISTANCE,
                    1
                ),
                driver.MAX_FINISH_SPEED
            )
        # If slowdown_node is None
        else:
            return driver.MAX_SPEED
        

def get_slowdown_node(current_node_index, path, is_circuit: bool=False, iteration=0):
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
        if node_angle_deg <= driver.ANGLE_DETECTION_THRESHOLD:
            # Check if there are ANGLE_DETECTION_COUNT nodes in front of this before calculating
            if i >= (len(path) - driver.ANGLE_DETECTION_COUNT):
                continue
            # Get sum of next angles
            cur_angle_detection_sum_deg = 0
            for j in range(i, i + driver.ANGLE_DETECTION_COUNT):
                ba_vector = Vector2(path[j-1].position.x - path[j].position.x, path[j-1].position.z - path[j].position.z)
                bc_vector = Vector2(path[j+1].position.x - path[j].position.x, path[j+1].position.z - path[j].position.z)
                cur_node_angle_rad = calculate_angle_between_2_vectors(ba_vector, bc_vector)
                cur_node_angle_deg = math.degrees(cur_node_angle_rad)
                cur_angle_detection_sum_deg += 180 - cur_node_angle_deg
            cur_angle_detection_sum_deg = 180 - cur_angle_detection_sum_deg
            #print(f'(GNSN) - I: {i}, Angles_Sum_Deg: {cur_angle_detection_sum_deg}')
            if cur_angle_detection_sum_deg <= driver.BRAKE_ANGLE:
                return path[i], SlowdownType.BRAKE
            
            elif cur_angle_detection_sum_deg <= driver.SLOWDOWN_ANGLE:
                return path[i], SlowdownType.SLOWDOWN
            
    # If its a circuit and didnt find any turn node, start again from beggining of path
    if is_circuit:
        if iteration < 1:
            return(get_slowdown_node(0, path, is_circuit, iteration+1))
        return None, None
    # Return last node in path to brake when finish
    return path[-1], SlowdownType.FINISH


def get_navi_node_and_vector(current_node_index, path: List[PathNode]):
        cur_navi = None
        if current_node_index < len(path)-1:
            next_node_id = path[current_node_index+1].node_id
            for adj_node in path[current_node_index].adj_nodes.values():
                if adj_node['node_id'] == next_node_id:
                    cur_navi = Navi.from_dict(adj_node['navi'])
                    direction_vector = path[current_node_index+1].position - path[current_node_index].position
                    direction_vector = Vector2(direction_vector.x, direction_vector.z)
                    return cur_navi, direction_vector
        return None, None
                

def get_lane_offset_based_on_navi(navi_node: Navi, direction: Vector2, preffered_lane: int=2):
    angle_difference = calculate_angle_between_2_vectors(navi_node.direction, direction)
    angle_difference = math.degrees(angle_difference)

    r_lanes, l_lanes = int(flags_data_extractor(navi_node.flags, 11, 13)), int(flags_data_extractor(navi_node.flags, 8, 10))
    
    preffered_lane -= 1 # Remap preffered lane if its 1 it will be 0, if its 2 it will be 1 etc
    if angle_difference < 90:
        if l_lanes > 1:
            return -2.5 + (preffered_lane*5)
        return 2.5
    else:
        if r_lanes > 1:
            return 2.5 - (preffered_lane*5)
        return -2.5


def apply_lane_offset_to_node(path_node: PathNode, node_direction: Vector2, offset: float):
    node_angle = vector_to_angle(node_direction)
    node_angle = math.degrees(node_angle)

    perpendicular_node_angle = node_angle - 90

    path_node.position += Vector3(math.cos(perpendicular_node_angle)*offset, 0, math.sin(perpendicular_node_angle)*offset)

    return path_node


def throttle_control(cur_speed: float, target_speed: float):
    if cur_speed < target_speed:
        key_down(ord('W'))
        key_up(ord('S'))
    else:
        key_up(ord('W'))
        speed_difference = cur_speed - target_speed
        if speed_difference > driver.BRAKING_SPEED_DIFFERENCE_THRESHOLD:
            key_down(ord('S'))


def direction_control(driver_to_node_angle: float):
    if driver_to_node_angle.__abs__() > driver.ANGLE_DIFFERENCE_THRESHOLD:           
        if driver_to_node_angle > 0:
            key_down(ord('D'))
            key_up(ord('A'))
        else:
            key_down(ord('A'))
            key_up(ord('D'))
    else:
        key_up(ord('D'))
        key_up(ord('A'))