def SolveTableNode():
    def __init__(self, shortest_dist, previous_node):
        self.shortest_dist = float(shortest_dist)
        self.previous_node = previous_node
    
    def to_dict(self):
        return {
            "shortest_distance": self.shortest_dist,
            "previous_node": self.previous_node
        }
    
    @classmethod
    def from_dict(cls, dict):
        return cls(dict["shortest_distance"],
                   dict["previous_node"])