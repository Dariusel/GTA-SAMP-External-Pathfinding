from enum import Enum

from resources.utils.vectors import Vector3, Vector2

class PathNode():
	def __init__(self, position=None, adj_nodes=None, node_id=None, area_id=None, node_type=None, flags=None, optional = {}):
		self.position = position
		self.adj_nodes = adj_nodes
		self.node_id = int(node_id) if not isinstance(node_id, int) else node_id
		self.area_id = int(area_id) if not isinstance(area_id, int) else area_id
		self.node_type = int(node_type) if node_type is not None else node_type # 1,2,3,4[...] Belongs to type of node (cars, race-tracks, boats)
		self.flags = int(flags) if flags is not None else flags
		self.optional = optional

	def to_dict(self):
		return {
			"position":{
				"x": self.position.x,
				"y": self.position.y,
				"z": self.position.z
			},
			"adj_nodes": self.adj_nodes,
			"node_id": self.node_id,
			"area_id": self.area_id,
			"node_type": self.node_type,
			"flags": self.flags,
			"optional": self.optional
		}
	
	def __str__(self):
		adj_nodes_str = '\n'.join(str(adj) for adj in self.adj_nodes.values())

		return (
		# Main Info
		f'=~=~=~=~   Node {self.node_id}   ~=~=~=~=\n'
        f'Pos: ({self.position.x}, {self.position.y}, {self.position.z}), '
        f'ID: {self.node_id}, '
        f'Area: {self.area_id}, '
        f'Type: {self.node_type}, '
        f'Flags: {self.flags}\n\n'
		
		# Adj Info
		f'Adjacent Nodes:\n'
		f'{adj_nodes_str}\n\n'
    )
	
	@classmethod
	def from_dict(cls, dict_data):
		return cls(
			 Vector3(dict_data["position"]["x"], dict_data["position"]["y"], dict_data["position"]["z"]),
			 dict_data["adj_nodes"],
			 dict_data["node_id"],
			 dict_data["area_id"],
			 dict_data["node_type"],
			 dict_data["flags"],
			 dict_data["optional"])
	
	@classmethod
	def get_closest_node_to_pos(cls, nodes_data, position):
		closest_node = None
		closest_node_distance = float('inf')

		for node in nodes_data.values():
			node_obj = cls.from_dict(node)
			node_pos = Vector3(node_obj.position.x, node_obj.position.y, node_obj.position.z)

			node_distance = Vector3.distance(node_pos, position)

			if node_distance < closest_node_distance:
				closest_node = node_obj
				closest_node_distance = node_distance

		return closest_node
			


class Navi():
	def __init__(self, position: Vector2, node_id: int, direction: Vector2, flags: str, optional = {}):
		self.position = position
		self.node_id = node_id
		self.direction = direction
		self.flags = flags
		self.optional = optional

	def to_dict(self):
		return {
			"position":{
				"x": self.position.x,
				"y": self.position.y
			},
			"node_id": self.node_id,
			"direction":{
				"x": self.direction.x,
				"y": self.direction.y
			},
			"flags": self.flags,
			"optional": self.optional
		}

	def __str__(self):
		return(
			f'Pos: ({self.position.x}, {self.position.y}), '
			f'ID: {self.node_id}, '
			f'Direction: ({self.direction.x}, {self.direction.y}), '
			f'Flags: {self.flags}'
		)
	
	@classmethod
	def from_dict(cls, dict_data):
		return cls(
			Vector2(dict_data["position"]["x"], dict_data["position"]["y"]),
			dict_data["node_id"],
			Vector2(dict_data["direction"]["x"], dict_data["direction"]["y"]),
			dict_data["flags"],
			dict_data["optional"])



class Link():
	def __init__(self, area_id, node_id):
		self.area_id = area_id
		self.node_id = node_id

	def to_dict(self):
		return {
			"area_id": self.area_id,
			"node_id": self.node_id
		}



class AdjacentNode():
	def __init__(self, node_id = None, link_length = None, navi:Navi = None, optional = {}):
		self.node_id = int(node_id) if node_id != None else node_id
		self.link_length = int(link_length) if link_length != None else link_length
		self.navi = navi
		self.optional = optional
	
	def to_dict(self):
		return {
			"node_id": self.node_id,
			"link_length": self.link_length,
			"navi": self.navi.to_dict(),
			"optional": self.optional
		}
	
	def __str__(self):
		return(
			# Adj Info
			f'ID: {self.node_id}, '
			f'Link-Length: {self.link_length}, '
			
			# Navi Info
			f'{self.navi}'
		)
	
	@classmethod
	def from_dict(cls, dict_data):
		return cls(
			dict_data["node_id"],
			dict_data["link_length"],
			dict_data["navi"],
			dict_data["optional"])


class NodeType(Enum):
	PathNodes = 'cars'
	Peds = 'peds'
	Navi = 'navi'
	Links = 'link'
	NaviLinks = 'navl'
	LinkLengths = 'lnkl'

	End = 'end'

	def __repr__(self):
		return self.value
	


class SlowdownType(Enum):
	BRAKE = 0
	SLOWDOWN = 1
	FINISH = 2
