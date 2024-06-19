from enum import Enum
from resources.utils.vectors import Vector3, Vector2

class PathNode():
	def __init__(self, position=None, adj_nodes=None, node_id=None, link_id_start=None, link_id_end=None, area_id=None, node_type=None, flags=None):
		self.position = position
		self.adj_nodes = adj_nodes
		self.node_id = int(node_id) if not isinstance(node_id, int) else node_id
		self.link_id_start = int(link_id_start) if link_id_start is not None else link_id_start
		self.link_id_end = int(link_id_end) if link_id_end is not None else link_id_end
		self.area_id = int(area_id) if area_id is not None else area_id
		self.node_type = int(node_type) if node_type is not None else node_type
		self.flags = int(flags) if flags is not None else flags

	def to_dict(self):
		return {
			"position":{
				"x": self.position.x,
				"y": self.position.y,
				"z": self.position.z
			},
			"adj_nodes": self.adj_nodes,
			"node_id": self.node_id,
			"link_id_start": self.link_id_start,
			"link_id_end": self.link_id_end,
			"area_id": self.area_id,
			"node_type": self.node_type,
			"flags": self.flags
		}
	
	@classmethod
	def from_dict(cls, dict_data):
		return cls(
			 Vector3(dict_data["position"]["x"], dict_data["position"]["y"], dict_data["position"]["z"]),
			 dict_data["adj_nodes"],
			 dict_data["node_id"],
			 dict_data["link_id_start"],
			 dict_data["link_id_end"],
			 dict_data["area_id"],
			 dict_data["node_type"],
			 dict_data["flags"])
	
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
	def __init__(self, area_id = None, node_id = None, link_length = None):
		self.area_id = int(area_id) if area_id != None else area_id
		self.node_id = int(node_id) if node_id != None else node_id
		self.link_length = int(link_length) if link_length != None else link_length
	
	def to_dict(self):
		return {
			"area_id": self.area_id,
			"node_id": self.node_id,
			"link_length": self.link_length
		}
	
	@classmethod
	def from_dict(cls, dict_data):
		return cls(
			dict_data["area_id"],
			dict_data["node_id"],
			dict_data["link_length"])



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
