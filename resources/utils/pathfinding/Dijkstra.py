from resources.utils.pathfinding.utils.dijkstra_classes import SolveTableNode
from resources.utils.nodes_classes import PathNode, AdjacentNode
from resources.utils.vectors import Vector3

import sys
import time



def pathfind_dijkstra(nodes_data, start_node, end_node): #nodes_arr = [PathNode()] | start_node = PathNode() | end_node = PathNode()
    start_time = time.time()
    solve_table = {} 

    open_nodes = {} # To visit
    closed_nodes = {} # Explored                                                     

    # start_node end_node to_dict()
    start_node = PathNode(start_node) if not isinstance(start_node, PathNode) else start_node
    end_node = PathNode(end_node) if not isinstance(end_node, PathNode) else end_node

    # Assign open_nodes
    for node_id, node in nodes_data.items():
        solve_table[node_id] = SolveTableNode('inf', None).to_dict()
    
    # Change start_node shortest_dist to 0 because its the origin
    solve_table[str(start_node.node_id)] = SolveTableNode('0', None).to_dict()
    
    # Set start_node as only open_nodes[] (Starting point)
    open_nodes[str(start_node.node_id)] = start_node.to_dict()
    


    # --- Solve with dijkstra ---
    while open_nodes:
        # Get node with the shortest distance in open_nodes and make that the current current_node
        shortest_dist = float('inf')
        current_node = None

        for node in open_nodes.values():
            node_obj = PathNode.from_dict(node)
            solve_table_node = SolveTableNode.from_dict(solve_table[str(node_obj.node_id)])

            if solve_table_node.distance <= shortest_dist:
                shortest_dist = solve_table_node.distance
                current_node = node_obj


        # Solve adjacent nodes for the previously calculated node (shortest_dist_node)
        for adj_node in current_node.adj_nodes.values():
            adj_node_obj = AdjacentNode.from_dict(adj_node)

            # Continue if adj_node is explored
            if str(adj_node_obj.node_id) in closed_nodes.keys():
                continue

            # Add adj_node to open_nodes for next iteration
            if str(adj_node_obj.node_id) not in open_nodes.keys():
                open_nodes[str(adj_node_obj.node_id)] = nodes_data[str(adj_node_obj.node_id)]

            # Variables for better readability
            current_node_solve_table = SolveTableNode.from_dict(solve_table[str(current_node.node_id)])
            adj_node_solve_table = SolveTableNode.from_dict(solve_table[str(adj_node_obj.node_id)])

            # Modify adj_node values in solve_table if new path distance is better then last one
            adj_node_dist = current_node_solve_table.distance + adj_node_obj.link_length
            if current_node.node_id == start_node.node_id:
                adj_node_solve_table.previous_node = current_node

            if adj_node_dist < adj_node_solve_table.distance:
                adj_node_solve_table.distance = adj_node_dist
                adj_node_solve_table.previous_node = current_node
            
            # Update solve_table values
            solve_table[str(adj_node_obj.node_id)] = adj_node_solve_table.to_dict()

        open_nodes.pop(str(current_node.node_id))
        closed_nodes[str(current_node.node_id)] = current_node

        # Exit loop if end_node reached
        if current_node.node_id == end_node.node_id:
            break
    

    # --- LOGGING ---
    finish_time = round(time.time() - start_time, 3)
    print(f'Finished in: {finish_time}')

    # Solution
    solved_path = [] # PathNode[]
    cur_solve_table_node = SolveTableNode.from_dict(solve_table[str(end_node.node_id)])

    while cur_solve_table_node.previous_node != None:
        solved_path.append(cur_solve_table_node.previous_node)
        cur_solve_table_node = SolveTableNode.from_dict(solve_table[str(cur_solve_table_node.previous_node.node_id)])

    return(solved_path[::-1])
    

    #for solve_table_node_id, solve_table_node in solve_table.items():
    #    solve_table_node = SolveTableNode.from_dict(solve_table_node)
    #    
    #    if solve_table_node.previous_node != None:
    #        print(f'{solve_table_node_id} -> {solve_table_node.distance}, {solve_table_node.previous_node.node_id}')
    #        continue
            