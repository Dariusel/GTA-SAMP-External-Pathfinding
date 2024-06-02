from enum import Enum

class Node():
	def __init__(self, position, nodeID, linkID, flags):
		self.position = position
		self.nodeID = nodeID
		self.linkID = linkID
		self.flags = flags


class NodeType(Enum):
	Cars = 'cars'
	Peds = 'peds'
	Navi = 'navi'
	Links = 'link'
	NaviLinks = 'navl'
	LinkLengths = 'lnkl'

	End = 'end'

	def __str__(self):
		return self.value