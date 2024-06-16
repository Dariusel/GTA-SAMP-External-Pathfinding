from PIL import Image
from resources.utils.vectors import Vector3

MAP_SIZE = 6000 # 6000x6000

def image_to_ingame_coords(vector3, mapImg):
    imgSize = mapImg.size[0]
    image_to_ingame_ratio = MAP_SIZE / imgSize #6000 is the size of ingame map

    # Formula for conversion
    x = vector3.x*image_to_ingame_ratio - MAP_SIZE/2
    z = MAP_SIZE - (MAP_SIZE/2 + vector3.z*image_to_ingame_ratio)

    return Vector3(x, vector3.y, z)
    

def ingame_to_image_coords(vector3, mapImg):
    imgSize = mapImg.size[0]
    ingame_to_image_ratio = imgSize / MAP_SIZE #6000 is the size of ingame map
    
    # Formula for conversion
    x = imgSize/2 + vector3.x*ingame_to_image_ratio
    z = imgSize - (imgSize/2 + vector3.z*ingame_to_image_ratio)

    return Vector3(x, vector3.y, z)