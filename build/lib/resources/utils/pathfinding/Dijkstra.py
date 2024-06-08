from resources.utils.pathfinding.utils.dijkstra_classes import SolveTableNode
from resources.utils.nodes_classes import PathNode
from resources.utils.vectors import Vector3




def pathfind_dijkstra(nodes_arr, start_node, finish_node): #nodes_arr = [PathNode()] | start_node = PathNode() | end_node = PathNode()
    solve_table = {}
    #print(jutils.NODES_DATA_JSON)


    open_nodes = [] # Visited nodes
    closed_nodes = [] # Unvisited nodes

    open_nodes.insert(0, start_node) # Add start_node first in open_nodes

    # Assign open_nodes
    for node_int, node in enumerate(nodes_arr):
        open_nodes.append(node)

        #solve_table[str(node_int)] = SolveTableNode('inf', None).to_dict()
    
    for node in solve_table.values():
        print(node)