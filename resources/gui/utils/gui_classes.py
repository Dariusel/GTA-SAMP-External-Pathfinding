from resources.utils.vectors import Vector3

class GuidingMarker():
    def __init__(self, canvas_id, ingame_pos: Vector3):
        self.canvas_id = canvas_id
        self.ingame_pos = ingame_pos

    
    def to_dict(self):
        return {
            "canvas_id": self.canvas_id,
            "ingame_pos": self.ingame_pos
        }

    @classmethod
    def from_dict(cls, dict):
        return cls(
            dict["canvas_id"],
            dict["ingame_pos"]
        )