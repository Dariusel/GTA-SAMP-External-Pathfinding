from resources.utils.json_utils import load_json, NODES_DATA_JSON
from resources.utils.pathfinding.Dijkstra import pathfind_dijkstra
from resources.utils.nodes_classes import PathNode

start_node = {'position': {'x': -2519.625, 'y': 28.5, 'z': -2174.75}, 'adj_nodes': {'Adjacent 0': {'area_id': 0, 'node_id': 1945, 'link_length': 22}, 'Adjacent 1': {'area_id': 0, 'node_id': 1605, 'link_length': 28}}, 'node_id': 1606, 'link_id_start': 6, 'link_id_end': 8, 'area_id': 8, 'node_type': 1, 'flags': 991234}
end_node = {'position': {'x': -1684.25, 'y': 47.375, 'z': -2673.0}, 'adj_nodes': {'Adjacent 0': {'area_id': 0, 'node_id': 209, 'link_length': 68}, 'Adjacent 1': {'area_id': 0, 'node_id': 320, 'link_length': 33}}, 'node_id': 319, 'link_id_start': 235, 'link_id_end': 237, 'area_id': 1, 'node_type': 1, 'flags': 991234}

if __name__ == '__main__':
    nodes_data = load_json(NODES_DATA_JSON)

    pathfind_dijkstra(nodes_data, PathNode.from_dict(start_node), PathNode.from_dict(end_node))