from PIL import Image
from matplotlib import pyplot as plt

from utils.vectors import Vector2, Vector3
from utils.file_paths import NODES_DATA_JSON, SOLVED_PATH_NODES_DATA, NODES_DATA_DETAILED_JSON
from utils.nodes_classes import PathNode, Navi
from utils.map_conversions import ingame_to_image_coords, image_to_ingame_coords
from resources.utils import json_utils


MAP_PATH = 'data/map/map.png' # 6144x6144 pixels in this example

MAP_LOGS = 'data/nodes_data/debug/map_logs.json'



def display_map(nodes_array_1=None, nodes_array_2={}):
    map_img = Image.open(MAP_PATH)

    fig, ax = plt.subplots()
    plt.imshow(map_img)

    if nodes_array_1:
        for node in nodes_array_1:
            node_pos_image = ingame_to_image_coords(Vector3(node.x, 0, node.y), map_img)
            plt.plot(node_pos_image.x, node_pos_image.z, 'r.', markersize=2)
    if nodes_array_2:
        for node in nodes_array_2:
            node_pos_image = ingame_to_image_coords(Vector3(node.x, 0, node.y), map_img)
            plt.plot(node_pos_image.x, node_pos_image.z, 'g.', markersize=2)

    fig.canvas.mpl_connect('button_press_event', on_figure_click)

    plt.show()


def on_figure_click(event):
    click_pos = Vector3(event.xdata, 0, event.ydata)
    map_img = Image.open(MAP_PATH)
    click_pos_ingame = image_to_ingame_coords(click_pos, map_img).round()

    clicked_node = PathNode.get_closest_node_to_pos(nodes_data, click_pos_ingame)

    print(clicked_node)


def get_nodes_data(nodes_percent=100, only_display_nodes=[], only_display_segments=[]): # For performance reasons set nodes_percent to a lower number to only aquire that % of nodes
    # Changeable variables
    only_display_nodes = []#[(33, 14870), (33, 14763)] # Format (x, y) x = Area ID, y = Node ID
    only_display_segments = [] # Format [a,b,c...] where a,b,c = Area ID(segment)


    # Do not modify variables
    nodes_data = json_utils.load_json(NODES_DATA_JSON)

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


            if (node_obj.area_id, node_obj.node_id) in only_display_nodes:
                nodes_to_add.append((node_id, node))
                continue
        
        # Only display segments
        elif len(only_display_segments) != 0:
            nodes_to_remove.append(node_id) # Remove all then add

            if node_obj.area_id in only_display_segments:
                nodes_to_add.append((node_id, node))
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


def get_navi_pos_array(nodes_data):
    navis_pos_array = []

    for segment in nodes_data['navi'].values():
        for navi in segment.values():
            navi_pos = navi["position"] 
            navis_pos_array.append(Vector2(float(navi_pos["x"]), float(navi_pos["y"])))
    
    return navis_pos_array


if __name__ == '__main__':
    nodes_data = get_nodes_data(nodes_percent=100)
    nodes_pos_array = get_nodes_pos_array(nodes_data)

    #display_map(nodes_pos_array)

    # Display navi nodes
    navis_data = json_utils.load_json(NODES_DATA_DETAILED_JSON)
    navis_pos_array = get_navi_pos_array(navis_data)

    display_map(nodes_pos_array)
