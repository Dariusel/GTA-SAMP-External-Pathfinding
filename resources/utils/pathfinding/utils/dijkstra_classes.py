class SolveTableNode():
    def __init__(self, distance, previous_node):
        self.distance = float(distance)
        self.previous_node = previous_node
    
    def to_dict(self):
        return {
            "distance": self.distance,
            "previous_node": self.previous_node
        }
    
    @classmethod
    def from_dict(cls, dict):
        return cls(dict["distance"],
                   dict["previous_node"])

