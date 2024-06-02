from PIL import Image
from matplotlib import pyplot as plt
from utils.vectors import Vector2, Vector3
from utils.nodes_classes import Node
from utils.map_conversions import ingame_to_image_coords, image_to_ingame_coords
import json

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
    print(image_to_ingame_coords(click_pos, MAP_PATH))

    clicked_node, segment = get_closest_node_to_click(click_pos)
    print(f'Clicked node(position: {clicked_node.position}, node_id: {clicked_node.nodeID}, link_id: {clicked_node.linkID}, flags: {clicked_node.flags}), {segment}')


def get_closest_node_to_click(click_pos):
    closest_node = None
    closest_node_distance = float('inf')
    
    for segment_id, segment in nodes_data['cars'].items():
        for node_data in segment.values():
            node = Node(Vector3(node_data['position']['x'], node_data['position']['y'], node_data['position']['z']),
                        node_data['node_id'],
                        node_data['link_id'],
                        node_data['flags'])
            
            node_pos = Vector2(node.position.x, node.position.z)
            node_distance = Vector2.distance(node_pos, click_pos)

            if node_distance < closest_node_distance:
                closest_node_distance = node_distance
                closest_node = node
                segment_name = segment_id
    return closest_node, segment_id


def get_nodes_data(nodes_percent=100): # For performance reasons set nodes_percent to a lower number to only aquire that % of nodes
    with open(NODES_DATA, 'r') as file:
        nodes_data = json.load(file)

    nodes_to_remove = []

    total_nodes = sum(len(segment) for segment in nodes_data["cars"].values())
    target_nodes = int(total_nodes * (nodes_percent / 100))
    step_size = total_nodes / target_nodes # Skip every 'step_size' count

    nodes_step_count = 0

    for segment_id, segment in nodes_data["cars"].items():
         for node_id, node in segment.items(): 
            # Skip this node if nodes_percent is met
            nodes_step_count += 1

            if nodes_step_count < step_size:
                nodes_to_remove.append((segment_id, node_id))
                continue

            nodes_step_count = 0 + (nodes_step_count - step_size)

    for segment_id, node_id in nodes_to_remove:
        nodes_data["cars"][segment_id].pop(node_id)

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
