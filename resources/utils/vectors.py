import math

class Vector3():
    def __init__(self, x: float, y: float, z: float):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    
    
    def __repr__(self):
        return f'({self.x}, {self.y}, {self.z})'
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def round(self, digits=2):
        return Vector3(round(self.x, digits), round(self.y, digits), round(self.z, digits))

    @staticmethod
    def distance(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)
    

class Vector2():
    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)
    
    
    def __repr__(self):
        return f'({self.x}, {self.y})'
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def distance(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def round(self, digits=2):
        return Vector2(round(self.x, digits), round(self.y, digits))