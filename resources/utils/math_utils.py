import math
from resources.utils.vectors import Vector3, Vector2

def calculate_look_at_angle(observer_pos: Vector3, observer_orientation, target_pos: Vector3):
    observer_orientation_degrees = math.degrees(observer_orientation)

    observer_pos_vector2 = Vector2(observer_pos.x, observer_pos.z)
    target_pos_vector2 = Vector2(target_pos.x, target_pos.z)

    opposite = target_pos_vector2.y - observer_pos_vector2.y
    adjacent = target_pos_vector2.x - observer_pos_vector2.x

    calculated_angle_rad = math.atan2(opposite, adjacent)
    calculated_angle_degrees = math.degrees(calculated_angle_rad)


    # Convert observer_orientation_degrees from [0,360] to [-180, 180]
    if observer_orientation_degrees <= 180:
        observer_orientation_degrees_180_range = observer_orientation_degrees
    elif observer_orientation_degrees > 180:
        observer_orientation_degrees_180_range = -(360 - observer_orientation_degrees)
        
    # Some if statements to determine if clockwise/counterclockwise rotation is faster
    calculated_angle_degrees = observer_orientation_degrees_180_range - calculated_angle_degrees
    if calculated_angle_degrees > 180:
        calculated_angle_degrees = -(360-calculated_angle_degrees)
    elif calculated_angle_degrees < -180:
        calculated_angle_degrees = 360-calculated_angle_degrees.__abs__()

    calculated_angle_rad = math.radians(calculated_angle_degrees)
    return calculated_angle_rad
