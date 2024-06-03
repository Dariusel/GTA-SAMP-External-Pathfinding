from PIL import Image
from matplotlib import pyplot as plt
import json

from utils.vectors import Vector2, Vector3
from utils.nodes_classes import PathNode
from utils.map_conversions import ingame_to_image_coords, image_to_ingame_coords

MAP_PATH = 'resources/Map Visualiser/map.png' # 6144x6144 pixels in this example

NODES_DATA = 'resources/nodes_data.json'


def display_map(nodes_array=None):
    mapImg = Image.open(MAP_PATH)

    fig, ax = plt.subplots()
    plt.imshow(mapImg)

    if nodes_array:
        for node in nodes_array:
            node_pos = ingame_to_image_coords(Vector2(node.x, node.y), MAP_PATH)
            plt.plot(node_pos.x, node_pos.y, 'r.')

    fig.canvas.mpl_connect('button_press_event', on_figure_click)

    plt.show()


def on_figure_click(event):
    click_pos = Vector2(event.xdata, event.ydata)
    click_pos_ingame = image_to_ingame_coords(click_pos, MAP_PATH).round()

    clicked_node = get_closest_node_to_click(click_pos_ingame)

    print(clicked_node.to_dict())


def get_closest_node_to_click(click_pos):
    closest_node = None
    closest_node_distance = float('inf')
    
    for segment in nodes_data['cars'].values():
        for node_data in segment.values():
            node = PathNode.from_dict(node_data)
            
            node_pos = Vector2(node.position.x, node.position.z)
            node_distance = round(Vector2.distance(node_pos, click_pos), 2)

            if node_distance < closest_node_distance:
                closest_node_distance = node_distance
                closest_node = node

    return closest_node


def get_nodes_data(nodes_percent=100): # For performance reasons set nodes_percent to a lower number to only aquire that % of nodes
    # Changeable variables
    only_display_nodes = [] # Format (x, y) x = Area ID, y = Node ID
    only_display_segments = [] # Format [a,b,c...] where a,b,c = Area ID(segment)


    
    # Do not modify variables
    with open(NODES_DATA, 'r') as file:
        nodes_data = json.load(file)

    total_nodes = sum(len(segment) for segment in nodes_data["cars"].values())
    target_nodes = int(total_nodes * (nodes_percent / 100))
    step_size = total_nodes / target_nodes # Skip every 'step_size' count

    nodes_step_count = 0

    nodes_to_remove = []
    nodes_to_add = [] 

    for segment_id, segment in nodes_data["cars"].items():
         for node_id, node in segment.items():
            # Only display these nodes if 'only_display_nodes[]' isnt empty
            if len(only_display_nodes) != 0:
                nodes_to_remove.append((segment_id, node_id))
                for node_to_display in only_display_nodes:
                    x, y = node_to_display
                    if (segment_id, node_id) == (f'Segment {x}', f'Node {y}'):
                        nodes_to_add.append((segment_id, node_id, node))
                        break

            # TODO - Only display these segments if 'only_display_segments[]' isnt empty
            #elif len(only_display_segments) != 0:
            #    for segment_to_display in only_display_segments:
                    

            else:
                # NODES_PERCENT Skips the current node if necessary
                nodes_step_count += 1
                if nodes_step_count < step_size:
                    nodes_to_remove.append((segment_id, node_id))
                    continue 

                nodes_step_count = 0 + (nodes_step_count - step_size)

    for segment_id, node_id in nodes_to_remove:
        nodes_data["cars"][segment_id].pop(node_id)
    
    for segment_id, node_id, node in nodes_to_add:
        nodes_data["cars"][segment_id][node_id] = node

    #endregion

    return nodes_data


def get_nodes_pos_array(nodes_data):
    nodes_pos_array = []

    for segment in nodes_data["cars"].values():
         for node in segment.values(): 
            node_pos = node["position"] 
            nodes_pos_array.append(Vector2(float(node_pos["x"]), float(node_pos["z"])))
    
    return nodes_pos_array



if __name__ == '__main__':
    nodes_data = get_nodes_data(10)
    nodes_pos_array = get_nodes_pos_array(nodes_data)

    display_map(nodes_pos_array)
