from PIL import Image
from .vectors import Vector2

MAP_SIZE = 6000 # 6000x6000

def image_to_ingame_coords(vector2, mapImg):
    img = Image.open(mapImg)
    imgSize = img.size[0]
    image_to_ingame_ratio = MAP_SIZE / imgSize #6000 is the size of ingame map

    # Formula for conversion
    x = vector2.x*image_to_ingame_ratio - MAP_SIZE/2
    y = MAP_SIZE - (MAP_SIZE/2 + vector2.y*image_to_ingame_ratio)

    return Vector2(x, y)
    

def ingame_to_image_coords(vector2, mapImg):
    img = Image.open(mapImg)
    imgSize = img.size[0]
    ingame_to_image_ratio = imgSize / MAP_SIZE #6000 is the size of ingame map
    
    # Formula for conversion
    x = imgSize/2 + vector2.x*ingame_to_image_ratio
    y = imgSize - (imgSize/2 + vector2.y*ingame_to_image_ratio)

    return Vector2(x, y)