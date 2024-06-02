from enum import Enum
from utils.vectors import Vector3
from utils.nodes_classes import Node, NodeType
import json
import math

TO_PARSE_FILE = 'resources/unprocessed/readable nodes.dnf'

OUTPUT_FILE = 'resources/nodes_data.json'


def parse_dnf_file(file_path):
	with open(file_path, 'r') as file:
		content = file.readlines()
	
	cur_category = None
	cur_segment = None

	nodes = []

	data = {}

	for x, line in enumerate(content):
		line = line.strip()

		# Check category
		for category in NodeType:
			if line == NodeType.End.value:
				cur_category = None
				cur_segment = None
				continue

			if line == category.value:
				cur_category = category

				data[str(cur_category)] = {}
				continue

		# Check segment
		if line.startswith('segment'):
			line_content = line.split()
			cur_segment = line_content[1]

			data[str(cur_category)][f"Segment {cur_segment}"] = {}
			continue

		# Skip if line is { or }
		if line == "{":
			continue
		elif line == "}":
			cur_segment = None
			continue

		# If the current line is a node, add it to the 'nodes[]' array
		if (cur_category == NodeType.Cars) and cur_segment != None: 
			line_content = line.split('|')
			
			cur_node = Node(
				Vector3(line_content[0], line_content[2], line_content[1]), 
				line_content[4], 
				line_content[3],
				line_content[7]
				)
			
			nodes.append(cur_node)

			node = {
				"position": {
					"x": cur_node.position.x,
					"y": cur_node.position.y,
					"z": cur_node.position.z
				},
				"node_id": cur_node.nodeID,
				"link_id": cur_node.linkID,
				"flags": cur_node.flags
			}

			data[str(cur_category)][f"Segment {cur_segment}"][f"Node {line_content[4]}"] = node
	
	with open(OUTPUT_FILE, 'w') as json_file:
		json.dump(data, json_file, indent=2)
			

if __name__ == '__main__':
	parse_dnf_file(TO_PARSE_FILE)
