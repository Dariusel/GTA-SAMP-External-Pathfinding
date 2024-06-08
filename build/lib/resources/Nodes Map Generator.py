from PIL import Image
from matplotlib import pyplot as plt

from utils.vectors import Vector2
from utils.json_utils import NODES_DATA_JSON
from utils.nodes_classes import PathNode
from utils.map_conversions import ingame_to_image_coords, image_to_ingame_coords
from resources.utils import json_utils


MAP_PATH = 'data/map/map.png' # 6144x6144 pixels in this example



def display_map(nodes_array=None):
    mapImg = Image.open(MAP_PATH)

    fig, ax = plt.subplots()
    plt.imshow(mapImg)

    if nodes_array:
        for node in nodes_array:
            node_pos = ingame_to_image_coords(Vector2(node.x, node.y), MAP_PATH)
            plt.plot(node_pos.x, node_pos.y, 'r.', markersize=2)

    fig.canvas.mpl_connect('button_press_event', on_figure_click)

    plt.show()


def on_figure_click(event):
    click_pos = Vector2(event.xdata, event.ydata)
    click_pos_ingame = image_to_ingame_coords(click_pos, MAP_PATH).round()

    clicked_node = get_closest_node_to_click(click_pos_ingame)

    print(f'ID: {clicked_node[0]}\n{clicked_node[1].to_dict()}')


def get_closest_node_to_click(click_pos):
    closest_node = None
    closest_node_distance = float('inf')
    
    for node_id, node in nodes_data.items():
        node = PathNode.from_dict(node)
        
        node_pos = Vector2(node.position.x, node.position.z)
        node_distance = round(Vector2.distance(node_pos, click_pos), 2)
        if node_distance < closest_node_distance:
            closest_node_distance = node_distance
            closest_node = (node_id, node)

    return closest_node


def get_nodes_data(nodes_percent=100, only_display_nodes=[], only_display_segments=[]): # For performance reasons set nodes_percent to a lower number to only aquire that % of nodes
    # Changeable variables
    only_display_nodes = [] # Format (x, y) x = Area ID, y = Node ID
    only_display_segments = [] # Format [a,b,c...] where a,b,c = Area ID(segment)


    # Do not modify variables
    nodes_data = json_utils.load_json(json_utils.NODES_DATA_JSON)

    total_nodes = sum(len(segment) for segment in nodes_data.values())
    target_nodes = int(total_nodes * (nodes_percent / 100))
    step_size = total_nodes / target_nodes # Skip every 'step_size' count

    nodes_step_count = 0

    nodes_to_remove = []
    nodes_to_add = [] 

    for node_id, node in nodes_data.items():
        node_obj = PathNode.from_dict(node)

        #Only display nodes
        if len(only_display_nodes) != 0:
            nodes_to_remove.append(node_id) # Remove all nodes then add

            for x, y in only_display_nodes:
                if (node_obj.area_id, node_obj.node_id) == (x, y):
                    nodes_to_add.append((node_id, node))
                    continue
            continue
        
        # Only display segments
        elif len(only_display_segments) != 0:
            nodes_to_remove.append(node_id) # Remove all then add

            for segment_id in only_display_segments:
                if segment_id == node_obj.area_id:
                    nodes_to_add.append((node_id, node))
                    continue
            
            continue
        
        # Display only % percent nodes
        elif nodes_percent != 100:
            if nodes_step_count >= step_size:
                nodes_step_count -= step_size
                continue
            
            nodes_to_remove.append(node_id) # Remove all nodes then add
            nodes_step_count += 1


    for node_id in nodes_to_remove:
        nodes_data.pop(node_id)

    for node_id, node in nodes_to_add:
        nodes_data[str(node_id)] = node

    return nodes_data


def get_nodes_pos_array(nodes_data):
    nodes_pos_array = []

    for node in nodes_data.values():
        node_pos = node["position"] 
        nodes_pos_array.append(Vector2(float(node_pos["x"]), float(node_pos["z"])))
    
    return nodes_pos_array



if __name__ == '__main__':
    nodes_data = get_nodes_data(10)
    nodes_pos_array = get_nodes_pos_array(nodes_data)

    display_map(nodes_pos_array)
