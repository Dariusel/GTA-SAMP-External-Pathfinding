from enum import Enum
import json

from utils.vectors import Vector3
from utils.json_utils import DNF_FILE, NODES_DATA_JSON, NODES_DATA_DETAILED_JSON
from utils.nodes_classes import PathNode, NodeType, Link, AdjacentNode
from utils.binary_utils import flags_data_extractor



def parse_dnf_file(file_path):
	supported_node_types = (NodeType.PathNodes.value, NodeType.Links.value, NodeType.LinkLengths.value)

	cur_node_index = 0

	cur_category = None
	cur_segment = None

	data = {}



	with open(file_path, 'r') as file:
		content = file.readlines()

	for x, line in enumerate(content):
		line = line.strip()

		# Check Category
		if line == NodeType.End.value:
			cur_category = None
			cur_segment = None
			continue
		elif line in supported_node_types:
			cur_category = line
			data[cur_category] = {}
			continue

		# Check Segment
		if line.startswith('segment') and cur_category in supported_node_types:
			line_content = line.split()
			cur_segment = line_content[1]

			data[cur_category][f"Segment {cur_segment}"] = {}
			continue

		# Skip if line is { or }
		if line == "{":
			cur_node_index = 0
			continue
		elif line == "}":
			cur_segment = None
			continue



		# Parse based on category
		if cur_category == NodeType.PathNodes.value and cur_segment != None:  # Path Nodes
			line_content = line.split('|')

			# Skip node parsing if node type != 1(roads)
			if line_content[6] != '1':
				continue
			
			adj_nodes_amount = flags_data_extractor(line_content[7], 0, 3)
			link_id_end = int(line_content[3]) + adj_nodes_amount

			# Get adj nodes info

			cur_node = PathNode(
				Vector3(line_content[0], line_content[2], line_content[1]), # POS
				None, # Adj Nodes
				line_content[4], # Node ID
				line_content[3], # Link ID Start
				link_id_end, # Link ID End
				cur_segment, # Area ID(Segment)
				line_content[6], # Node Type
				line_content[7] # Flags
				).to_dict()

			data[cur_category][f"Segment {cur_segment}"][f"Node {line_content[4]}"] = cur_node

		# Link Nodes
		elif (cur_category == NodeType.Links.value) and cur_segment != None:
			line_content = line.split('|')

			link_node = Link(line_content[0], line_content[1]).to_dict()

			data[cur_category][f"Segment {cur_segment}"][f"Link {cur_node_index}"] = link_node
			cur_node_index += 1

		# Link Lengths
		elif (cur_category == NodeType.LinkLengths.value) and cur_segment != None:
			line_content = line

			link_length_node = {"length": int(line)}

			data[cur_category][f"Segment {cur_segment}"][f"Length {cur_node_index}"] = link_length_node
			cur_node_index += 1
		
		
	# Assign adj nodes (This is done after all parsing/loading into memory to ensure that links and linkLengths categories exist)
	for segment_id, segment in data[NodeType.PathNodes.value].items():
		for node_id, node in segment.items():
			node_obj = PathNode.from_dict(node)

			# To not write dict path every time
			links_dict = data[NodeType.Links.value][f"Segment {node_obj.area_id}"]
			lengths_dict = data[NodeType.LinkLengths.value][f"Segment {node_obj.area_id}"]

			# Add adjacent data to PathNode
			adj_nodes = {}
			for i, link in enumerate(range(node_obj.link_id_start, node_obj.link_id_end)):
				link_obj = AdjacentNode(
							links_dict[f"Link {link}"]["area_id"],
							links_dict[f"Link {link}"]["node_id"],
							lengths_dict[f"Length {link}"]["length"])
				
				adj_nodes[f"Adjacent {i}"] = link_obj.to_dict()
			
			data[NodeType.PathNodes.value][segment_id][node_id]["adj_nodes"] = adj_nodes
	
	# Write json_file_detailed
	with open(NODES_DATA_DETAILED_JSON, 'w') as json_file:
		json.dump(data, json_file, indent=2)


	# Write json_file_final
	data_final = {}

	# Optimization reasons
	lookup_table = {}
	long_node_id = 0
	for segment_id, segment in data[NodeType.PathNodes.value].items():
		for node_id, node in segment.items():
			data_final[long_node_id] = node
			data_final[long_node_id]['node_id'] = long_node_id

			lookup_table[(segment_id, node_id)] = node
			lookup_table[(segment_id, node_id)]['long_node_id'] = long_node_id
			long_node_id += 1

	# Update adj_nodes node_id to use the format without area_id(segments)
	for node_id, node in data_final.items():
		adj_nodes_path = data_final[node_id]['adj_nodes']

		for adj_id, adj_node in adj_nodes_path.items():
			x, y = f'Segment {adj_node['area_id']}', f'Node {adj_node['node_id']}'

			adj_nodes_path[adj_id]['node_id'] = lookup_table[(x, y)]['long_node_id']

	# Remove unnecessary values
	for node_id, node in data_final.items():
		data_final[node_id].pop('long_node_id')

		# TODO - Remove this from data_final without affecting other modules using the PathNode , it breaks the from_dict() func for example
		#data_final[node_id].pop('link_id_start')
		#data_final[node_id].pop('link_id_end')
		
		#for adj_node in data_final[node_id]['adj_nodes'].values():
		#	adj_node.pop('area_id')


	with open(NODES_DATA_JSON, 'w') as json_file:
		json.dump(data_final, json_file, indent=2)


	return 'Succesfully parsed data'
			


if __name__ == '__main__':
	parse_dnf_file(DNF_FILE)
