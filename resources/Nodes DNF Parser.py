from resources.utils.vectors import Vector3, Vector2
from resources.utils.json_utils import save_json
from resources.utils.file_paths import DNF_FILE, NODES_DATA_JSON, NODES_DATA_DETAILED_JSON
from resources.utils.nodes_classes import PathNode, NodeType, Link, AdjacentNode, Navi
from resources.utils.binary_utils import flags_data_extractor



def parse_line_based_on_category(data, line, cur_category, cur_segment, cur_node_index):
	# --- Path Nodes ---
	if cur_category == NodeType.PathNodes.value and cur_segment != None:
		line_content = line.split('|')

		# Skip node parsing if node type != 1(roads)
		if line_content[6] != '1':
			return
		
		adj_nodes_amount = flags_data_extractor(line_content[7], 0, 3)
		link_id_end = int(line_content[3]) + adj_nodes_amount

		cur_node_optional = {
			"area_id": cur_segment,
			"link_id_start": line_content[3],
			"link_id_end": link_id_end
		}

		cur_node = PathNode(
			Vector3(line_content[0], line_content[2], line_content[1]), # POS
			None, # Adj Nodes
			line_content[4], # Node ID
			line_content[6], # Node Type
			line_content[7], # Flags
			cur_node_optional # Optional Params
			).to_dict()
		
		data[cur_category][f"Segment {cur_segment}"][f"Node {line_content[4]}"] = cur_node

	# --- Navi Nodes ---
	elif (cur_category == NodeType.Navi.value) and cur_segment != None:
		line_content = line.split('|')

		navi_optional = {
			"area_id": line_content[2]
		}

		navi_node = Navi(
			Vector2(line_content[0], line_content[1]),
			line_content[3],
			Vector2(line_content[4], line_content[5]),
			line_content[6],
			navi_optional
		).to_dict()
		
		data[cur_category][f"Segment {cur_segment}"][f"Node {cur_node_index}"] = navi_node

		return cur_node_index + 1

	# --- Link Nodes ---
	elif (cur_category == NodeType.Links.value) and cur_segment != None:
		line_content = line.split('|')

		link_node = Link(line_content[0], line_content[1]).to_dict()

		data[cur_category][f"Segment {cur_segment}"][f"Link {cur_node_index}"] = link_node

		return cur_node_index + 1

	# --- Navi Links ---
	elif (cur_category == NodeType.NaviLinks.value) and cur_segment != None:
		line_content = line.strip()

		navi_link = {
			"node_area_id": int(line_content) # 2b - UINT16 - lower 10 bit are the Navi Node ID, upper 6 bit the corresponding Area ID
		}

		data[cur_category][f"Segment {cur_segment}"][f"Navi Link {cur_node_index}"] = navi_link

		return cur_node_index + 1

	# --- Link Lengths ---
	elif (cur_category == NodeType.LinkLengths.value) and cur_segment != None:
		line_content = line

		link_length_node = {"length": int(line)}

		data[cur_category][f"Segment {cur_segment}"][f"Length {cur_node_index}"] = link_length_node

		return cur_node_index + 1



def assign_adjacent_nodes_after_parse(data):
	for segment_id, segment in data[NodeType.PathNodes.value].items():
		for node_id, node in segment.items():
			node_obj = PathNode.from_dict(node)

			# To not write dict path every time
			links_dict = data[NodeType.Links.value][f"Segment {node_obj.optional['area_id']}"]
			lengths_dict = data[NodeType.LinkLengths.value][f"Segment {node_obj.optional['area_id']}"]

			navi_nodes_dict = data[NodeType.Navi.value]
			navi_links_dict = data[NodeType.NaviLinks.value][f"Segment {node_obj.optional['area_id']}"]

			# Add adjacent data to PathNode
			adj_nodes = {}

			link_id_start = int(node_obj.optional['link_id_start'])
			link_id_end = int(node_obj.optional['link_id_end'])
			for i, link in enumerate(range(link_id_start, link_id_end)):
				adj_navi_link_area_node_id = navi_links_dict[f"Navi Link {link}"]["node_area_id"]

				adj_navi_node_id = flags_data_extractor(adj_navi_link_area_node_id, 0, 9)
				adj_navi_area_id = flags_data_extractor(adj_navi_link_area_node_id, 9, 15)

				adj_navi_obj = Navi.from_dict(navi_nodes_dict[f"Segment {adj_navi_area_id}"][f"Node {adj_navi_node_id}"])


				adj_optional = {
					"area_id": links_dict[f"Link {link}"]["area_id"]
				}

				adj_obj = AdjacentNode(
							links_dict[f"Link {link}"]["node_id"],
							lengths_dict[f"Length {link}"]["length"],
							adj_navi_obj,
							adj_optional)
				
				adj_nodes[f"Adjacent {i}"] = adj_obj.to_dict()
			
			data[NodeType.PathNodes.value][segment_id][node_id]["adj_nodes"] = adj_nodes



def create_final_data(data):
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
	# TODO - Also make adj_nodes navi components use the format without area_id
	for node_id, node in data_final.items():
		adj_nodes_path = data_final[node_id]['adj_nodes']

		for adj_id, adj_node in adj_nodes_path.items():
			x, y = f'Segment {adj_node['optional']['area_id']}', f'Node {adj_node['node_id']}'

			adj_nodes_path[adj_id]['node_id'] = lookup_table[(x, y)]['long_node_id']
			
			navi_node_path = adj_nodes_path[adj_id]['navi']
			x, y = f'Segment {navi_node_path['optional']['area_id']}', f'Node {navi_node_path['node_id']}'
			navi_node_path['node_id'] = lookup_table[(x, y)]['long_node_id']

	# Remove unnecessary values
	for node_id, node in data_final.items():
		data_final[node_id].pop('long_node_id')

		data_final[node_id]['optional'] = {}

		for adj_node in data_final[node_id]['adj_nodes'].values():
			adj_node['optional'] = {}
			adj_node['navi']['optional'] = {}
	
	return data_final



def parse_dnf_file(file_path):
	supported_node_types = (NodeType.PathNodes.value, NodeType.Navi.value, NodeType.Links.value, NodeType.NaviLinks.value, NodeType.LinkLengths.value)

	cur_node_index = 0

	cur_category = None
	cur_segment = None

	data = {}


	with open(file_path, 'r') as file:
		to_parse_content = file.readlines()

	for line in to_parse_content:
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

		cur_node_index = parse_line_based_on_category(data, line, cur_category, cur_segment, cur_node_index)
		
	# Assign adj nodes (This is done after all parsing/loading into memory to ensure that links and linkLengths categories exist)
	assign_adjacent_nodes_after_parse(data)
	
	# Write detailed JSON File containing everything
	save_json(data, NODES_DATA_DETAILED_JSON)

	# Write final JSON file containing only what pathfinding needs
	data_final = create_final_data(data)
	save_json(data_final, NODES_DATA_JSON)

	return 'Succesfully parsed data'
			


if __name__ == '__main__':
	parse_dnf_file(DNF_FILE)
