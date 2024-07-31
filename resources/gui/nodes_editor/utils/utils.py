import sys, os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))
from resources.utils.vectors import Vector3, Vector2



def get_canvas_crop_bbox(img_size, last_img_size, event_x, event_y, last_bbox, zoom, last_zoom):
    zoom_factor = img_size/512
    img_size_factor = img_size/last_img_size

    last_bbox = list(last_bbox)
    last_bbox[0] *= img_size_factor
    last_bbox[1] *= img_size_factor
    last_bbox[2] *= img_size_factor
    last_bbox[3] *= img_size_factor

    event_x *= zoom_factor
    event_y *= zoom_factor

    event_x /= last_zoom
    event_y /= last_zoom

    event_x = last_bbox[0] + event_x
    event_y = last_bbox[1] + event_y

    crop_radius = (img_size/2)/zoom
    x1 = event_x - crop_radius
    y1 = event_y - crop_radius
    x2 = event_x + crop_radius
    y2 = event_y + crop_radius

    # Zoom In
    if zoom > last_zoom:
        if x1 < last_bbox[0]:
            x2 += last_bbox[0] - x1
        if y1 < last_bbox[1]:
            y2 += last_bbox[1] - y1
        if x2 > last_bbox[2]:
            x1 -= (x2 - last_bbox[2])
        if y2 > last_bbox[3]:
            y1 -= (y2 - last_bbox[3])
        x1 = max(x1, last_bbox[0])
        y1 = max(y1, last_bbox[1])
        x2 = min(x2, last_bbox[2])
        y2 = min(y2, last_bbox[3])
    # Zoom Out
    else:
        if x1 < 0:
            x2 += abs(x1)
        if y1 < 0:
            y2 += abs(y1)
        if x2 > img_size:
            x1 -= (x2 - img_size)
        if y2 > img_size:
            y1 -= (y2 - img_size)
        x1 = max(x1, 0)
        y1 = max(y1, 0)
        x2 = min(x2, img_size)
        y2 = min(y2, img_size)

    return x1, y1, x2, y2



def get_zoomed_image_clicked_position(event_x, event_y, img_size, crop_bbox, zoom):
    zoom_factor = img_size/512

    x = event_x*zoom_factor
    y = event_y*zoom_factor

    x /= zoom
    y /= zoom

    x = crop_bbox[0] + x
    y = crop_bbox[1] + y

    return Vector3(x, 0, y)



def get_zoomed_image_xy_canvas_position(x, y, img_size, canvas_size, crop_bbox, zoom):
    x -= crop_bbox[0]
    y -= crop_bbox[1]

    canvas_scale = (img_size/zoom)/canvas_size
    canvas_x = x / canvas_scale
    canvas_y = y / canvas_scale

    return Vector3(canvas_x, 0, canvas_y)


def calculate_player_polygon(marker_size: float, position: Vector3, orientation_angle: float):
        point1_angle_rad = math.radians(orientation_angle)
        point2_angle_rad = point1_angle_rad + math.radians(140)
        point3_angle_rad = point1_angle_rad + math.radians(180)
        point4_angle_rad= point1_angle_rad - math.radians(140)
        
        #Point 1
        x1 = position.x + marker_size * math.cos(point1_angle_rad)
        z1 = position.z - marker_size * math.sin(point1_angle_rad)
        #Point 2
        x2 = position.x + marker_size * math.cos(point2_angle_rad)
        z2 = position.z - marker_size * math.sin(point2_angle_rad)
        #Point 3
        x3 = position.x + marker_size * (math.cos(point3_angle_rad) * 0.2)
        z3 = position.z - marker_size * (math.sin(point3_angle_rad) * 0.2)
        #Point 4
        x4 = position.x + marker_size * math.cos(point4_angle_rad)
        z4 = position.z - marker_size * math.sin(point4_angle_rad)

        return x1, z1, x2, z2, x3, z3, x4, z4


def is_inside_bbox_2d(position: Vector2, bbox: list[4]):
    if not bbox[0] < position.x < bbox[2]:
        return False
    if not bbox[1] > position.y > bbox[3]:
        return False
    
    return True
