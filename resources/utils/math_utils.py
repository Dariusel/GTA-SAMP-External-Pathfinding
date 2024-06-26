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


def calculate_angle_between_2_vectors(vec_a: Vector2, vec_b: Vector2): # Only horizontal angle doesnt care about y axis
    babc_dot = (vec_a.x*vec_b.x) + (vec_a.y*vec_b.y)

    ba_magnitude = math.sqrt(vec_a.x**2 + vec_a.y**2)
    bc_magnitude = math.sqrt(vec_b.x**2 + vec_b.y**2)

    # Limit cos_angle to [-1, 1]
    cos_angle = babc_dot/(ba_magnitude*bc_magnitude)
    cos_angle = max(-1, min(1, cos_angle))

    calculated_angle = math.acos(cos_angle)
    return calculated_angle

def vector_to_angle(vec: Vector2):
    return math.atan2(vec.y, vec.x)

def angle_to_vector(angle: float):
    return Vector2(math.cos(math.radians(angle)), math.sin(math.radians(angle)))