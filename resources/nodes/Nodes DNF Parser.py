from enum import Enum
from utils import Position
import json

TO_PARSE_FILE = 'resources/readable nodes.dnf'

OUTPUT_FILE = ''

# TEMP JSON Only
OUTPUT_JSON_FILE = 'resources/readable nodes.json'


class Node():
	def __init__(self, Position, NodeID, LinkID):
		self.Position = Position
		self.NodeID = NodeID
		self.LinkID = LinkID


class Category(Enum):
	Cars = 'cars'
	Peds = 'peds'
	Navi = 'navi'
	Links = 'link'
	NaviLinks = 'navl'
	LinkLengths = 'lnkl'

	End = 'end'

	def __str__(self):
		return self.value


def parse_dnf_file(file_path):
	with open(file_path, 'r') as file:
		content = file.readlines()
	
	cur_category = None
	cur_segment = None

	nodes = []

	# TEMP JSON Only
	data = {}

	for x, line in enumerate(content):
		line = line.strip()

		# Check category
		for category in Category:
			if line == Category.End.value:
				cur_category = None
				cur_segment = None
				continue

			if line == category.value:
				cur_category = category

				# TEMP JSON Only
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
		if (cur_category == Category.Cars or cur_category == Category.Peds or cur_category == Category.Navi) and cur_segment != None: 
			line_content = line.split('|')
			
			cur_node = Node(
				Position(line_content[0], line_content[2], line_content[1]), 
				line_content[4], 
				line_content[3])
			
			nodes.append(cur_node)
		
			# TEMP JSON Only
			node = {
				"position": {
					"x": line_content[0],
					"y": line_content[2],
					"z": line_content[1]
				},
				"node_id": line_content[4],
				"link_id": line_content[3]
			}

			data[str(cur_category)][f"Segment {cur_segment}"][f"Node {line_content[4]}"] = node
	
	with open(OUTPUT_JSON_FILE, 'w') as json_file:
		json.dump(data, json_file, indent=2)
			


parse_dnf_file(TO_PARSE_FILE)